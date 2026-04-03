"""
Business Validator - Layer 2
Validates business rules, formats, qualifiers, and cross-field consistency
"""
from typing import List
from ..models import ValidationError, ValidationContext, ErrorSeverity, ErrorLayer, ErrorType
from ..formats import (
    NPIValidator, DateValidator, AmountValidator,
    ZIPCodeValidator, ProcedureCodeValidator, ICD10Validator
)
from ..reference_data import get_code_set_loader


class BusinessValidator:
    """Layer 2: Validates business rules and data formats"""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.code_loader = get_code_set_loader()
    
    def validate(self, context: ValidationContext) -> List[ValidationError]:
        """Execute all business validations"""
        self.errors = []
        
        try:
            # Format validations
            self._validate_npi_fields(context)
            self._validate_date_fields(context)
            self._validate_amount_fields(context)
            self._validate_zip_codes(context)
            
            # Qualifier validations
            self._validate_qualifiers(context)
            
            # Cross-field validations
            self._validate_cross_field_consistency(context)
            
            # Transaction-specific validations
            if context.transaction_type == "837P":
                self._validate_837_specific(context)
            elif context.transaction_type == "835":
                self._validate_835_specific(context)
            elif context.transaction_type == "834":
                self._validate_834_specific(context)
            
        except Exception as e:
            self.errors.append(
                ValidationError(
                    layer=ErrorLayer.BUSINESS,
                    type=ErrorType.CROSS_FIELD,
                    severity=ErrorSeverity.ERROR,
                    segment="UNKNOWN",
                    error=f"Business validation error: {str(e)}",
                    suggestion="Review business rule validation logic"
                )
            )
        
        return self.errors
    
    def _validate_npi_fields(self, context: ValidationContext):
        """Validate all NPI fields in the transaction"""
        # Find all NM1 segments
        nm1_segments = context.get_all_segments("NM1")
        
        for idx, segment in enumerate(nm1_segments):
            # Get qualifier and ID value
            qualifier = None
            id_value = None
            
            if "elements" in segment:
                for element in segment["elements"]:
                    if element.get("position") == "08":
                        qualifier = element.get("value")
                    elif element.get("position") == "09":
                        id_value = element.get("value")
            
            # If we have a 10-digit numeric ID, it should be an NPI
            if id_value and len(id_value) == 10 and id_value.isdigit():
                # Validate NPI format and Luhn checksum
                is_valid, error_msg = NPIValidator.validate(id_value)
                
                if not is_valid:
                    self.errors.append(
                        ValidationError(
                            layer=ErrorLayer.BUSINESS,
                            type=ErrorType.FORMAT,
                            severity=ErrorSeverity.ERROR,
                            segment="NM1",
                            field="NM109",
                            error=error_msg,
                            suggestion=NPIValidator.get_suggestion(id_value),
                            fixable=False,
                            value=id_value,
                            code="NPI001"
                        )
                    )
    
    def _validate_date_fields(self, context: ValidationContext):
        """Validate all date fields"""
        # DTP segments contain dates
        dtp_segments = context.get_all_segments("DTP")
        
        for segment in dtp_segments:
            date_qualifier = None
            date_format = None
            date_value = None
            
            if "elements" in segment:
                for element in segment["elements"]:
                    pos = element.get("position")
                    if pos == "01":
                        date_qualifier = element.get("value")
                    elif pos == "02":
                        date_format = element.get("value")
                    elif pos == "03":
                        date_value = element.get("value")
            
            if date_value:
                # Determine if future dates are allowed
                # Most dates should NOT be in the future
                # Only allow future for specific qualifiers like effective dates
                future_allowed_qualifiers = ["303", "348", "349"]  # Future effective dates
                allow_future = date_qualifier in future_allowed_qualifiers
                check_dob = date_qualifier == "291"  # 291 = DOB
                
                format_type = "CCYYMMDD" if date_format == "D8" else "CCYYMMDD"
                
                is_valid, error_msg = DateValidator.validate(
                    date_value, 
                    format_type=format_type,
                    allow_future=allow_future,
                    check_dob=check_dob
                )
                
                if not is_valid:
                    self.errors.append(
                        ValidationError(
                            layer=ErrorLayer.BUSINESS,
                            type=ErrorType.FORMAT,
                            severity=ErrorSeverity.ERROR,
                            segment="DTP",
                            field="DTP03",
                            error=error_msg,
                            suggestion=DateValidator.get_suggestion(date_value, format_type),
                            fixable=True,
                            value=date_value,
                            code="DATE001"
                        )
                    )
        
        # DMG02 contains date of birth
        dmg_segments = context.get_all_segments("DMG")
        
        for segment in dmg_segments:
            dob = None
            
            if "elements" in segment:
                for element in segment["elements"]:
                    if element.get("position") == "02":
                        dob = element.get("value")
                        break
            
            if dob:
                is_valid, error_msg = DateValidator.validate(
                    dob, 
                    format_type="CCYYMMDD",
                    allow_future=False,
                    check_dob=True
                )
                
                if not is_valid:
                    self.errors.append(
                        ValidationError(
                            layer=ErrorLayer.BUSINESS,
                            type=ErrorType.FORMAT,
                            severity=ErrorSeverity.ERROR,
                            segment="DMG",
                            field="DMG02",
                            error=error_msg,
                            suggestion="Verify date of birth is in CCYYMMDD format and reasonable",
                            fixable=False,
                            value=dob,
                            code="DATE002"
                        )
                    )
    
    def _validate_amount_fields(self, context: ValidationContext):
        """Validate monetary amount fields"""
        # CLM02 - Total claim charge amount
        clm_segments = context.get_all_segments("CLM")
        
        for segment in clm_segments:
            amount = context.get_element_value("CLM", "02")
            
            if amount:
                is_valid, error_msg = AmountValidator.validate(
                    amount,
                    allow_negative=False,
                    allow_zero=False
                )
                
                if not is_valid:
                    self.errors.append(
                        ValidationError(
                            layer=ErrorLayer.BUSINESS,
                            type=ErrorType.FORMAT,
                            severity=ErrorSeverity.ERROR,
                            segment="CLM",
                            field="CLM02",
                            error=error_msg,
                            suggestion=AmountValidator.get_suggestion(amount),
                            fixable=True,
                            value=amount,
                            code="AMT001"
                        )
                    )
    
    def _validate_zip_codes(self, context: ValidationContext):
        """Validate ZIP code fields"""
        n4_segments = context.get_all_segments("N4")
        
        for segment in n4_segments:
            zip_code = None
            
            if "elements" in segment:
                for element in segment["elements"]:
                    if element.get("position") == "03":
                        zip_code = element.get("value")
                        break
            
            if zip_code:
                is_valid, error_msg = ZIPCodeValidator.validate(zip_code)
                
                if not is_valid:
                    self.errors.append(
                        ValidationError(
                            layer=ErrorLayer.BUSINESS,
                            type=ErrorType.FORMAT,
                            severity=ErrorSeverity.ERROR,
                            segment="N4",
                            field="N403",
                            error=error_msg,
                            suggestion="ZIP code must be 5 digits (XXXXX) or 9 digits with hyphen (XXXXX-XXXX)",
                            fixable=True,
                            value=zip_code,
                            code="ZIP001"
                        )
                    )
    
    def _validate_qualifiers(self, context: ValidationContext):
        """Validate qualifier codes using reference data"""
        # NM108 - Identification Code Qualifier
        valid_nm108_all = self.code_loader.get_qualifier_values("NM108")
        
        nm1_segments = context.get_all_segments("NM1")
        
        for segment in nm1_segments:
            qualifier = None
            id_value = None
            
            if "elements" in segment:
                for element in segment["elements"]:
                    pos = element.get("position")
                    if pos == "08":
                        qualifier = element.get("value")
                    elif pos == "09":
                        id_value = element.get("value")
            
            if qualifier and id_value:
                # Validate qualifier matches ID format
                id_length = len(id_value) if id_value else 0
                is_numeric = id_value.isdigit() if id_value else False
                
                # Rule 1: If ID is 10 digits, qualifier MUST be XX (NPI)
                if id_length == 10 and is_numeric:
                    if qualifier != "XX":
                        self.errors.append(
                            ValidationError(
                                layer=ErrorLayer.BUSINESS,
                                type=ErrorType.CODE,
                                severity=ErrorSeverity.ERROR,
                                segment="NM1",
                                field="NM108",
                                error=f"Invalid qualifier '{qualifier}' for 10-digit ID",
                                suggestion="Use XX for 10-digit NPI (National Provider Identifier)",
                                fixable=False,
                                value=qualifier,
                                code="QUAL001"
                            )
                        )
                
                # Rule 2: If qualifier is XX, ID MUST be 10 digits
                elif qualifier == "XX":
                    if id_length != 10 or not is_numeric:
                        self.errors.append(
                            ValidationError(
                                layer=ErrorLayer.BUSINESS,
                                type=ErrorType.CODE,
                                severity=ErrorSeverity.ERROR,
                                segment="NM1",
                                field="NM109",
                                error=f"Invalid NPI format: {id_value} (length: {id_length})",
                                suggestion="NPI must be exactly 10 numeric digits when using qualifier XX",
                                fixable=False,
                                value=id_value,
                                code="QUAL003"
                            )
                        )
                
                # Rule 3: If qualifier is 34 (SSN), ID should be 9 digits
                elif qualifier == "34":
                    if id_length != 9 or not is_numeric:
                        self.errors.append(
                            ValidationError(
                                layer=ErrorLayer.BUSINESS,
                                type=ErrorType.CODE,
                                severity=ErrorSeverity.WARNING,
                                segment="NM1",
                                field="NM109",
                                error=f"SSN format issue: {id_value} (length: {id_length})",
                                suggestion="SSN should be 9 numeric digits when using qualifier 34",
                                fixable=False,
                                value=id_value,
                                code="QUAL004"
                            )
                        )
                
                # Rule 4: Check if qualifier is valid
                if qualifier not in valid_nm108_all:
                    valid_list = ", ".join(sorted(valid_nm108_all)[:5])
                    self.errors.append(
                        ValidationError(
                            layer=ErrorLayer.BUSINESS,
                            type=ErrorType.CODE,
                            severity=ErrorSeverity.ERROR,
                            segment="NM1",
                            field="NM108",
                            error=f"Invalid identification code qualifier: {qualifier}",
                            suggestion=f"Use valid qualifier (e.g., {valid_list})",
                            fixable=False,
                            value=qualifier,
                            code="QUAL002"
                        )
                    )
    
    def _validate_cross_field_consistency(self, context: ValidationContext):
        """Validate consistency across fields"""
        # DOB vs Claim Date
        dob = context.get_element_value("DMG", "02")
        
        # Find service date from DTP segment with qualifier 434
        claim_date = None
        dtp_segments = context.get_all_segments("DTP")
        for segment in dtp_segments:
            qualifier = None
            date_value = None
            
            if "elements" in segment:
                for element in segment["elements"]:
                    if element.get("position") == "01":
                        qualifier = element.get("value")
                    elif element.get("position") == "03":
                        date_value = element.get("value")
            
            if qualifier == "434":  # Service date
                claim_date = date_value
                break
        
        if dob and claim_date:
            comparison = DateValidator.compare_dates(dob, claim_date)
            if comparison is not None and comparison >= 0:
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.BUSINESS,
                        type=ErrorType.CROSS_FIELD,
                        severity=ErrorSeverity.ERROR,
                        segment="DTP",
                        field="DTP03",
                        error="Service date must be after patient date of birth",
                        suggestion="Verify patient DOB and service date are correct",
                        fixable=False,
                        code="CROSS001"
                    )
                )
    
    def _validate_837_specific(self, context: ValidationContext):
        """837-specific validations"""
        # Validate claim total vs service line totals
        claim_total = context.get_element_value("CLM", "02")
        
        # Sum service line amounts
        service_line_total = 0
        sv1_segments = context.get_all_segments("SV1")
        
        for segment in sv1_segments:
            if "elements" in segment:
                for element in segment["elements"]:
                    if element.get("position") == "02":
                        line_amount = element.get("value")
                        if line_amount:
                            parsed = AmountValidator.parse_amount(line_amount)
                            if parsed:
                                service_line_total += parsed
        
        if claim_total:
            claim_total_parsed = AmountValidator.parse_amount(claim_total)
            if claim_total_parsed is not None and service_line_total > 0:
                if not AmountValidator.compare_amounts(str(claim_total_parsed), str(service_line_total)):
                    self.errors.append(
                        ValidationError(
                            layer=ErrorLayer.BUSINESS,
                            type=ErrorType.CROSS_FIELD,
                            severity=ErrorSeverity.ERROR,
                            segment="CLM",
                            field="CLM02",
                            error=f"Claim total (${claim_total_parsed}) does not match sum of service lines (${service_line_total})",
                            suggestion="Ensure CLM02 equals sum of all SV102 amounts",
                            fixable=True,
                            code="837001"
                        )
                    )
    
    def _validate_835_specific(self, context: ValidationContext):
        """835-specific validations"""
        # Validate CAS segment group codes
        valid_group_codes = ["CO", "PR", "OA", "PI", "CR"]
        
        cas_segments = context.get_all_segments("CAS")
        
        for segment in cas_segments:
            group_code = None
            
            if "elements" in segment:
                for element in segment["elements"]:
                    if element.get("position") == "01":
                        group_code = element.get("value")
                        break
            
            if group_code and group_code not in valid_group_codes:
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.BUSINESS,
                        type=ErrorType.CODE,
                        severity=ErrorSeverity.ERROR,
                        segment="CAS",
                        field="CAS01",
                        error=f"Invalid CAS group code: {group_code}",
                        suggestion=f"Use valid group code: {', '.join(valid_group_codes)}",
                        fixable=False,
                        value=group_code,
                        code="835001"
                    )
                )
    
    def _check_duplicate_members(self, context: ValidationContext):
        """Check for duplicate members in 834 transaction"""
        # Track members by SSN, Member ID, and Name+DOB
        seen_members = {}
        
        # Get all NM1 loops (member loops)
        nm1_segments = context.get_all_segments("NM1")
        
        for idx, nm1_segment in enumerate(nm1_segments):
            # Extract member identifiers
            member_id = None
            last_name = None
            first_name = None
            dob = None
            
            if "elements" in nm1_segment:
                for element in nm1_segment["elements"]:
                    pos = element.get("position")
                    if pos == "03":
                        last_name = element.get("value")
                    elif pos == "04":
                        first_name = element.get("value")
                    elif pos == "09":
                        member_id = element.get("value")
            
            # Find associated DMG segment for DOB
            # In 834, DMG follows NM1 in the same loop
            if idx < len(context.segments):
                for i in range(idx, min(idx + 10, len(context.segments))):
                    seg = context.segments[i]
                    if seg.get("segmentId") == "DMG":
                        if "elements" in seg:
                            for element in seg["elements"]:
                                if element.get("position") == "02":
                                    dob = element.get("value")
                                    break
                        break
            
            # Create unique key from available identifiers
            if member_id or (last_name and first_name and dob):
                # Check by member ID
                if member_id:
                    if member_id in seen_members:
                        self.errors.append(
                            ValidationError(
                                layer=ErrorLayer.BUSINESS,
                                type=ErrorType.CROSS_FIELD,
                                severity=ErrorSeverity.ERROR,
                                segment="NM1",
                                field="NM109",
                                error=f"Duplicate member ID detected: {member_id}",
                                suggestion="Each member must have a unique identifier",
                                fixable=False,
                                value=member_id,
                                code="834003"
                            )
                        )
                    else:
                        seen_members[member_id] = True
                
                # Check by name + DOB combination
                if last_name and first_name and dob:
                    name_dob_key = f"{last_name}|{first_name}|{dob}"
                    if name_dob_key in seen_members:
                        self.errors.append(
                            ValidationError(
                                layer=ErrorLayer.BUSINESS,
                                type=ErrorType.CROSS_FIELD,
                                severity=ErrorSeverity.WARNING,
                                segment="NM1",
                                error=f"Possible duplicate member: {first_name} {last_name} (DOB: {dob})",
                                suggestion="Verify this is not a duplicate enrollment",
                                fixable=False,
                                code="834004"
                            )
                        )
                    else:
                        seen_members[name_dob_key] = True
    
    def _validate_834_specific(self, context: ValidationContext):
        """834-specific validations using reference data"""
        # Validate INS segment codes
        valid_ins01 = self.code_loader.get_qualifier_values("INS01")
        valid_ins02 = self.code_loader.get_qualifier_values("INS02")
        valid_ins03 = self.code_loader.get_qualifier_values("INS03")
        valid_ins04 = self.code_loader.get_qualifier_values("INS04")
        
        ins_segments = context.get_all_segments("INS")
        
        for segment in ins_segments:
            ins01 = None
            ins02 = None
            ins03 = None
            ins04 = None
            
            if "elements" in segment:
                for element in segment["elements"]:
                    pos = element.get("position")
                    if pos == "01":
                        ins01 = element.get("value")
                    elif pos == "02":
                        ins02 = element.get("value")
                    elif pos == "03":
                        ins03 = element.get("value")
                    elif pos == "04":
                        ins04 = element.get("value")
            
            # INS01 - Member Indicator
            if ins01 and ins01 not in valid_ins01:
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.BUSINESS,
                        type=ErrorType.CODE,
                        severity=ErrorSeverity.ERROR,
                        segment="INS",
                        field="INS01",
                        error=f"Invalid member indicator: {ins01}",
                        suggestion=f"Use valid value: {', '.join(sorted(valid_ins01))}",
                        fixable=False,
                        value=ins01,
                        code="834001"
                    )
                )
            
            # INS02 - Relationship Code
            if ins02 and ins02 not in valid_ins02:
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.BUSINESS,
                        type=ErrorType.CODE,
                        severity=ErrorSeverity.ERROR,
                        segment="INS",
                        field="INS02",
                        error=f"Invalid relationship code: {ins02}",
                        suggestion=f"Use valid relationship code (e.g., 18=Self, 01=Spouse)",
                        fixable=False,
                        value=ins02,
                        code="834002"
                    )
                )
            
            # INS03 - Maintenance Type Code
            if ins03 and ins03 not in valid_ins03:
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.BUSINESS,
                        type=ErrorType.CODE,
                        severity=ErrorSeverity.ERROR,
                        segment="INS",
                        field="INS03",
                        error=f"Invalid maintenance type code: {ins03}",
                        suggestion=f"Use valid code (e.g., 021=Addition, 001=Change, 024=Termination)",
                        fixable=False,
                        value=ins03,
                        code="834005"
                    )
                )
            
            # INS04 - Maintenance Reason Code
            if ins04 and ins04 not in valid_ins04:
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.BUSINESS,
                        type=ErrorType.CODE,
                        severity=ErrorSeverity.ERROR,
                        segment="INS",
                        field="INS04",
                        error=f"Invalid maintenance reason code: {ins04}",
                        suggestion=f"Use valid reason code (e.g., XN=Non-Payment, 28=Initial Enrollment)",
                        fixable=False,
                        value=ins04,
                        code="834006"
                    )
                )
        
        # Duplicate member detection
        self._check_duplicate_members(context)
