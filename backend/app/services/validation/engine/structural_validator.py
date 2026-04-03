"""
Structural Validator - Layer 1
Validates EDI file structure, segments, and basic syntax
"""
from typing import List, Dict, Any
from ..models import ValidationError, ValidationContext, ErrorSeverity, ErrorLayer, ErrorType


class StructuralValidator:
    """Layer 1: Validates EDI structure and syntax"""
    
    # Required segments for each transaction type
    REQUIRED_SEGMENTS = {
        "837P": ["ISA", "GS", "ST", "BHT", "NM1", "SE", "GE", "IEA"],
        "835": ["ISA", "GS", "ST", "BPR", "SE", "GE", "IEA"],
        "834": ["ISA", "GS", "ST", "BGN", "SE", "GE", "IEA"]
    }
    
    def __init__(self):
        self.errors: List[ValidationError] = []
    
    def validate(self, context: ValidationContext) -> List[ValidationError]:
        """Execute all structural validations"""
        self.errors = []
        
        try:
            # Basic structure checks
            self._validate_envelope_structure(context)
            self._validate_required_segments(context)
            self._validate_segment_structure(context)
            self._validate_control_numbers(context)
            self._validate_segment_counts(context)
            self._validate_isa_gs_consistency(context)
            
        except Exception as e:
            self.errors.append(
                ValidationError(
                    layer=ErrorLayer.STRUCTURAL,
                    type=ErrorType.SEGMENT,
                    severity=ErrorSeverity.CRITICAL,
                    segment="UNKNOWN",
                    error=f"Critical structural validation error: {str(e)}",
                    suggestion="Check if file is properly formatted EDI"
                )
            )
        
        return self.errors
    
    def _validate_envelope_structure(self, context: ValidationContext):
        """Validate ISA/GS/ST envelope structure"""
        segments = context.segments
        
        if not segments:
            self.errors.append(
                ValidationError(
                    layer=ErrorLayer.STRUCTURAL,
                    type=ErrorType.SEGMENT,
                    severity=ErrorSeverity.CRITICAL,
                    segment="ISA",
                    error="No segments found in EDI file",
                    suggestion="Ensure file contains valid EDI segments",
                    hint="The file appears to be empty or not properly formatted as an EDI file. EDI files contain structured data segments separated by delimiters."
                )
            )
            return
        
        # Check ISA segment (must be first)
        if not segments or segments[0].get("segmentId") != "ISA":
            self.errors.append(
                ValidationError(
                    layer=ErrorLayer.STRUCTURAL,
                    type=ErrorType.SEGMENT,
                    severity=ErrorSeverity.CRITICAL,
                    segment="ISA",
                    error="ISA segment must be first segment in file",
                    suggestion="Add ISA interchange control header",
                    hint="Every EDI file must start with an ISA segment, which acts like an envelope header containing sender and receiver information."
                )
            )
        
        # Check IEA segment (must be last)
        if segments and segments[-1].get("segmentId") != "IEA":
            self.errors.append(
                ValidationError(
                    layer=ErrorLayer.STRUCTURAL,
                    type=ErrorType.SEGMENT,
                    severity=ErrorSeverity.ERROR,
                    segment="IEA",
                    error="IEA segment must be last segment in file",
                    suggestion="Add IEA interchange control trailer",
                    hint="Every EDI file must end with an IEA segment, which closes the envelope and confirms how many transactions were included."
                )
            )
        
        # Check for GS/GE pair
        has_gs = any(seg.get("segmentId") == "GS" for seg in segments)
        has_ge = any(seg.get("segmentId") == "GE" for seg in segments)
        
        if has_gs and not has_ge:
            self.errors.append(
                ValidationError(
                    layer=ErrorLayer.STRUCTURAL,
                    type=ErrorType.SEGMENT,
                    severity=ErrorSeverity.ERROR,
                    segment="GE",
                    error="GS segment found but missing GE trailer",
                    suggestion="Add GE functional group trailer",
                    hint="The GS segment starts a functional group (a collection of related transactions), and every GS must have a matching GE segment to close it."
                )
            )
        
        # Check for ST/SE pair
        has_st = any(seg.get("segmentId") == "ST" for seg in segments)
        has_se = any(seg.get("segmentId") == "SE" for seg in segments)
        
        if has_st and not has_se:
            self.errors.append(
                ValidationError(
                    layer=ErrorLayer.STRUCTURAL,
                    type=ErrorType.SEGMENT,
                    severity=ErrorSeverity.ERROR,
                    segment="SE",
                    error="ST segment found but missing SE trailer",
                    suggestion="Add SE transaction set trailer",
                    hint="The ST segment starts a transaction (like an enrollment or claim), and every ST must have a matching SE segment to close it and count the segments."
                )
            )
    
    def _validate_required_segments(self, context: ValidationContext):
        """Check if all required segments are present"""
        transaction_type = context.transaction_type
        required = self.REQUIRED_SEGMENTS.get(transaction_type, [])
        
        segment_ids = {seg.get("segmentId") for seg in context.segments}
        
        for required_seg in required:
            if required_seg not in segment_ids:
                # Create segment-specific hints
                segment_hints = {
                    "ISA": "ISA is the Interchange Control Header - it's like the outer envelope of your EDI file containing sender/receiver info.",
                    "GS": "GS is the Functional Group Header - it groups related transactions together (like multiple enrollments).",
                    "ST": "ST is the Transaction Set Header - it marks the start of a specific transaction (like one enrollment or claim).",
                    "BGN": "BGN is the Beginning Segment - it provides basic information about when and why this transaction was created.",
                    "BHT": "BHT is the Beginning of Hierarchical Transaction - it identifies the purpose and type of the healthcare transaction.",
                    "BPR": "BPR is the Financial Information segment - it contains payment amount and method details for remittance advice.",
                    "SE": "SE is the Transaction Set Trailer - it closes the transaction and counts how many segments were included.",
                    "GE": "GE is the Functional Group Trailer - it closes the functional group and counts how many transactions were included.",
                    "IEA": "IEA is the Interchange Control Trailer - it closes the entire EDI file and confirms the interchange control number."
                }
                
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.STRUCTURAL,
                        type=ErrorType.SEGMENT,
                        severity=ErrorSeverity.ERROR,
                        segment=required_seg,
                        error=f"Required segment {required_seg} is missing",
                        suggestion=f"Add {required_seg} segment to transaction",
                        hint=segment_hints.get(required_seg, f"The {required_seg} segment is required for this transaction type.")
                    )
                )
    
    def _validate_segment_structure(self, context: ValidationContext):
        """Validate individual segment structure"""
        for idx, segment in enumerate(context.segments):
            segment_id = segment.get("segmentId")
            
            if not segment_id:
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.STRUCTURAL,
                        type=ErrorType.SEGMENT,
                        severity=ErrorSeverity.ERROR,
                        segment="UNKNOWN",
                        line_number=idx + 1,
                        error="Segment missing identifier",
                        suggestion="Ensure segment has valid ID"
                    )
                )
                continue
            
            # Check minimum element count for critical segments
            element_count = len(segment.get("elements", []))
            
            if segment_id == "ISA" and element_count < 16:
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.STRUCTURAL,
                        type=ErrorType.SEGMENT,
                        severity=ErrorSeverity.CRITICAL,
                        segment="ISA",
                        line_number=idx + 1,
                        error=f"ISA segment must have 16 elements (found {element_count})",
                        suggestion="Verify ISA segment structure",
                        hint="The ISA segment requires exactly 16 data elements including authorization info, sender/receiver IDs, date, time, standards version, and control numbers. Some elements may be missing or incorrectly formatted."
                    )
                )
            
            elif segment_id == "GS" and element_count < 8:
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.STRUCTURAL,
                        type=ErrorType.SEGMENT,
                        severity=ErrorSeverity.ERROR,
                        segment="GS",
                        line_number=idx + 1,
                        error=f"GS segment must have 8 elements (found {element_count})",
                        suggestion="Verify GS segment structure",
                        hint="The GS segment requires exactly 8 data elements including functional code, sender/receiver codes, date, time, control number, and version. Some elements may be missing."
                    )
                )
    
    def _validate_control_numbers(self, context: ValidationContext):
        """Validate control numbers match between headers and trailers"""
        # ISA/IEA control number
        isa_control = context.get_element_value("ISA", "13")
        iea_control = context.get_element_value("IEA", "02")
        
        if isa_control and iea_control and isa_control != iea_control:
            self.errors.append(
                ValidationError(
                    layer=ErrorLayer.STRUCTURAL,
                    type=ErrorType.CROSS_FIELD,
                    severity=ErrorSeverity.ERROR,
                    segment="IEA",
                    field="IEA02",
                    error=f"IEA control number ({iea_control}) does not match ISA ({isa_control})",
                    suggestion="Ensure ISA13 and IEA02 have matching control numbers",
                    hint="Control numbers are like tracking IDs - the number at the start (ISA) must match the number at the end (IEA) to confirm the file is complete and unchanged."
                )
            )
        
        # GS/GE control number
        gs_control = context.get_element_value("GS", "06")
        ge_control = context.get_element_value("GE", "02")
        
        if gs_control and ge_control and gs_control != ge_control:
            self.errors.append(
                ValidationError(
                    layer=ErrorLayer.STRUCTURAL,
                    type=ErrorType.CROSS_FIELD,
                    severity=ErrorSeverity.ERROR,
                    segment="GE",
                    field="GE02",
                    error=f"GE control number ({ge_control}) does not match GS ({gs_control})",
                    suggestion="Ensure GS06 and GE02 have matching control numbers",
                    hint="The functional group control number at the start (GS) must match the one at the end (GE) to confirm all transactions in the group are accounted for."
                )
            )
        
        # ST/SE control number
        st_control = context.get_element_value("ST", "02")
        se_control = context.get_element_value("SE", "02")
        
        if st_control and se_control and st_control != se_control:
            self.errors.append(
                ValidationError(
                    layer=ErrorLayer.STRUCTURAL,
                    type=ErrorType.CROSS_FIELD,
                    severity=ErrorSeverity.ERROR,
                    segment="SE",
                    field="SE02",
                    error=f"SE control number ({se_control}) does not match ST ({st_control})",
                    suggestion="Ensure ST02 and SE02 have matching control numbers",
                    hint="The transaction control number at the start (ST) must match the one at the end (SE) to confirm this specific transaction is complete."
                )
            )
    
    def _validate_segment_counts(self, context: ValidationContext):
        """Validate segment counts in trailers"""
        # Count segments between ST and SE
        st_index = -1
        se_index = -1
        
        for idx, seg in enumerate(context.segments):
            if seg.get("segmentId") == "ST":
                st_index = idx
            elif seg.get("segmentId") == "SE":
                se_index = idx
                break
        
        if st_index >= 0 and se_index > st_index:
            # Count segments between ST and SE (inclusive)
            actual_count = se_index - st_index + 1
            se_count = context.get_element_value("SE", "01")
            
            if se_count and str(actual_count) != str(se_count):
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.STRUCTURAL,
                        type=ErrorType.CROSS_FIELD,
                        severity=ErrorSeverity.ERROR,
                        segment="SE",
                        field="SE01",
                        error=f"SE segment count ({se_count}) does not match actual count ({actual_count})",
                        suggestion=f"Update SE01 to {actual_count}",
                        hint=f"The SE segment should report how many segments are in this transaction (including ST and SE). It says {se_count} but there are actually {actual_count} segments.",
                        fixable=True
                    )
                )
    
    def _validate_isa_gs_consistency(self, context: ValidationContext):
        """Validate ISA and GS version consistency"""
        # ISA12 - Interchange Control Version Number
        isa_version = context.get_element_value("ISA", "12")
        
        # GS08 - Version/Release/Industry Identifier Code
        gs_version = context.get_element_value("GS", "08")
        
        if isa_version and gs_version:
            # Clean ISA version (may have extra characters like ^)
            isa_clean = isa_version.split("^")[-1] if "^" in isa_version else isa_version
            
            # Check if ISA version is valid
            if isa_clean not in ["00401", "00501"]:
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.STRUCTURAL,
                        type=ErrorType.FORMAT,
                        severity=ErrorSeverity.ERROR,
                        segment="ISA",
                        field="ISA12",
                        error=f"Invalid ISA version: {isa_version}",
                        suggestion="Use valid version (00401 or 00501)",
                        hint="The ISA version indicates which EDI standard is being used. Common versions are 00401 (version 4010) and 00501 (version 5010). The version provided is not recognized.",
                        fixable=False,
                        value=isa_version
                    )
                )
            
            # Check if GS version matches ISA version
            # ISA 00501 should match GS 005010X... format
            if isa_clean == "00501" and not gs_version.startswith("00501"):
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.STRUCTURAL,
                        type=ErrorType.CROSS_FIELD,
                        severity=ErrorSeverity.ERROR,
                        segment="GS",
                        field="GS08",
                        error=f"GS version ({gs_version}) does not match ISA version ({isa_version})",
                        suggestion="Ensure ISA12 and GS08 versions are consistent (e.g., ISA=00501, GS=005010X220A1)",
                        hint="The version numbers in ISA and GS must be compatible. If ISA uses version 00501, then GS should use a 005010X format (like 005010X220A1 for 834 transactions).",
                        fixable=False
                    )
                )
            elif isa_clean == "00401" and not gs_version.startswith("00401"):
                self.errors.append(
                    ValidationError(
                        layer=ErrorLayer.STRUCTURAL,
                        type=ErrorType.CROSS_FIELD,
                        severity=ErrorSeverity.ERROR,
                        segment="GS",
                        field="GS08",
                        error=f"GS version ({gs_version}) does not match ISA version ({isa_version})",
                        suggestion="Ensure ISA12 and GS08 versions are consistent (e.g., ISA=00401, GS=004010X098A1)",
                        hint="The version numbers in ISA and GS must be compatible. If ISA uses version 00401, then GS should use a 004010X format.",
                        fixable=False
                    )
                )
