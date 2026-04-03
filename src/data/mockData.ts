export interface EDIElement {
  value: string;
}

export interface EDISegment {
  id: string;
  segmentId: string;
  elements: EDIElement[];
}

export interface EDISession {
  sessionId: string;
  transactionType: string;
  status: 'processed' | 'errors' | 'fixed';
  filename: string;
  createdAt: string;
  segments: EDISegment[];
}

export interface EDIError {
  id: string;
  segmentId: string;
  segmentName: string;
  message: string;
  severity: 'low' | 'medium' | 'high';
}

export const mockSession: EDISession = {
  sessionId: "sess_mock_1234",
  transactionType: "837",
  status: "errors",
  filename: "claims_2026_04.edi",
  createdAt: "2026-04-03T10:00:00Z",
  segments: [
    {
      id: "seg_1",
      segmentId: "ISA",
      elements: [{ value: "00" }, { value: "          " }, { value: "00" }, { value: "          " }, { value: "ZZ" }, { value: "SENDER" }, { value: "ZZ" }, { value: "RECEIVER" }, { value: "260403" }, { value: "1000" }, { value: "U" }, { value: "00401" }, { value: "000000001" }, { value: "0" }, { value: "T" }, { value: ":" }]
    },
    {
      id: "seg_2",
      segmentId: "GS",
      elements: [{ value: "HC" }, { value: "SENDER" }, { value: "RECEIVER" }, { value: "20260403" }, { value: "1000" }, { value: "1" }, { value: "X" }, { value: "004010X098A1" }]
    },
    {
      id: "seg_3",
      segmentId: "ST",
      elements: [{ value: "837" }, { value: "0001" }]
    },
    {
      id: "seg_4",
      segmentId: "BHT",
      elements: [{ value: "0019" }, { value: "00" }, { value: "39203949302" }, { value: "20260403" }, { value: "1000" }, { value: "CH" }]
    },
    {
      id: "seg_5",
      segmentId: "NM1",
      elements: [{ value: "41" }, { value: "2" }, { value: "DOE HOSPITAL" }, { value: "" }, { value: "" }, { value: "" }, { value: "" }, { value: "46" }, { value: "123456789" }]
    },
    {
      id: "seg_6",
      segmentId: "NM1",
      elements: [{ value: "IL" }, { value: "1" }, { value: "SMITH" }, { value: "JOHN" }, { value: "A" }, { value: "" }, { value: "" }, { value: "MI" }, { value: "" }]
    }
  ]
};

export const mockErrors: EDIError[] = [
  {
    id: "err_1",
    segmentId: "seg_6",
    segmentName: "NM1",
    message: "Missing primary ID (NM109) when Identification Code Qualifier is 'MI'",
    severity: "high"
  }
];

export const mockRecentSessions = [
  { id: "1", filename: "claims_batch_A.edi", status: "processed", date: "2 Hours Ago" },
  { id: "2", filename: "claims_2026_04.edi", status: "errors", date: "4 Hours Ago" },
  { id: "3", filename: "payment_remit.edi", status: "fixed", date: "Yesterday" }
];
