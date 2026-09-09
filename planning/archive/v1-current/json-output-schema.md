# JSON Output Schema — Pain Point Analysis
**Last Updated:** 2026-04-21  
**Status:** Draft  
**Purpose:** Define the structured output format for the Formatter agent

---

## Schema Overview

The JSON output captures the complete pain point analysis, organized hierarchically from Lv2 down to individual pain points.

---

## JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PainPointAnalysisOutput",
  "description": "Structured output from the client pain point analysis workflow",
  "type": "object",
  "required": ["metadata", "summary", "analysis"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["lv1_area", "lv2_area", "analysis_date", "confidence"],
      "properties": {
        "lv1_area": {
          "type": "string",
          "description": "Level 1 category (e.g., '05.00 Source to Pay')"
        },
        "lv2_area": {
          "type": "string",
          "description": "Level 2 category being analyzed (e.g., '05.10 Purchasing/Payment Inquiries')"
        },
        "analysis_date": {
          "type": "string",
          "format": "date",
          "description": "Date of analysis in ISO 8601 format"
        },
        "confidence": {
          "type": "string",
          "enum": ["High", "Medium", "Low"],
          "description": "Overall confidence in the analysis"
        }
      }
    },
    "summary": {
      "type": "object",
      "required": ["lv2_score", "lv2_score_reason", "key_pain_points", "key_uplift_opportunity"],
      "properties": {
        "lv2_score": {
          "type": "string",
          "enum": ["No Challenges", "Some Challenges", "Significant Challenges"],
          "description": "Rolled-up RAG score at Lv2 level"
        },
        "lv2_score_reason": {
          "type": "string",
          "description": "Rationale for the Lv2 score"
        },
        "key_pain_points": {
          "type": "array",
          "items": { "type": "string" },
          "description": "List of key pain points identified"
        },
        "key_uplift_opportunity": {
          "type": "string",
          "description": "Primary uplift opportunity"
        },
        "total_pain_points_observed": {
          "type": "integer",
          "description": "Count of observed pain points"
        },
        "total_additional_pain_points": {
          "type": "integer",
          "description": "Count of additional pain points not in framework"
        }
      }
    },
    "analysis": {
      "type": "array",
      "description": "Detailed analysis by Lv3 category",
      "items": {
        "type": "object",
        "required": ["lv3_id", "lv3_name", "lv3_description", "lv3_score", "pain_points"],
        "properties": {
          "lv3_id": {
            "type": "string",
            "description": "Lv3 identifier (e.g., '05.10.01')"
          },
          "lv3_name": {
            "type": "string",
            "description": "Lv3 category name"
          },
          "lv3_description": {
            "type": "string",
            "description": "Lv3 category description"
          },
          "lv3_score": {
            "type": "string",
            "enum": ["No Challenges", "Some Challenges", "Significant Challenges"],
            "description": "Rolled-up RAG score at Lv3 level"
          },
          "lv3_score_reason": {
            "type": "string",
            "description": "Rationale for the Lv3 score"
          },
          "pain_points": {
            "type": "array",
            "items": {
              "$ref": "#/definitions/PainPoint"
            }
          }
        }
      }
    },
    "additional_pain_points": {
      "type": "array",
      "description": "Pain points identified in transcript but not in framework",
      "items": {
        "$ref": "#/definitions/AdditionalPainPoint"
      }
    }
  },
  "definitions": {
    "PainPoint": {
      "type": "object",
      "required": ["pain_point_id", "framework_pain_point", "observed"],
      "properties": {
        "pain_point_id": {
          "type": "string",
          "description": "Pain point identifier within Lv3"
        },
        "framework_pain_point": {
          "type": "string",
          "description": "Original pain point text from framework"
        },
        "observed": {
          "type": "boolean",
          "description": "Whether this pain point was observed in the transcript"
        },
        "client_specific_expression": {
          "type": "string",
          "description": "Pain point expressed using client's terminology (only if observed)"
        },
        "supporting_quotes": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Direct quotes from transcript supporting this pain point"
        },
        "uplift_opportunity": {
          "type": "string",
          "description": "Suggested improvement opportunity (only if observed)"
        },
        "score": {
          "type": "object",
          "description": "Scoring dimensions (only if observed)",
          "properties": {
            "relevance": {
              "type": "string",
              "enum": ["Medium", "High", "N/A"]
            },
            "urgency": {
              "type": "string",
              "enum": ["Medium", "High", "N/A"]
            },
            "frequency": {
              "type": "string",
              "enum": ["Medium", "High", "N/A"]
            },
            "opportunity": {
              "type": "string",
              "enum": ["Medium", "High", "N/A"]
            },
            "overall": {
              "type": "string",
              "enum": ["Medium", "High", "N/A"],
              "description": "Most frequent dimension score"
            }
          }
        }
      }
    },
    "AdditionalPainPoint": {
      "type": "object",
      "required": ["description", "supporting_quotes"],
      "properties": {
        "description": {
          "type": "string",
          "description": "Description of the additional pain point"
        },
        "supporting_quotes": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Direct quotes from transcript"
        },
        "suggested_lv3_alignment": {
          "type": "string",
          "description": "Which Lv3 category this might align with"
        },
        "uplift_opportunity": {
          "type": "string",
          "description": "Suggested improvement opportunity"
        }
      }
    }
  }
}
```

---

## Pydantic Model (for OpenAI Agents SDK)

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import date

class Confidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class RAGScore(str, Enum):
    NO_CHALLENGES = "No Challenges"
    SOME_CHALLENGES = "Some Challenges"
    SIGNIFICANT_CHALLENGES = "Significant Challenges"

class DimensionScore(str, Enum):
    MEDIUM = "Medium"
    HIGH = "High"
    NA = "N/A"

class PainPointScore(BaseModel):
    relevance: DimensionScore = DimensionScore.NA
    urgency: DimensionScore = DimensionScore.NA
    frequency: DimensionScore = DimensionScore.NA
    opportunity: DimensionScore = DimensionScore.NA
    overall: DimensionScore = DimensionScore.NA

class PainPoint(BaseModel):
    pain_point_id: str
    framework_pain_point: str
    observed: bool
    client_specific_expression: Optional[str] = None
    supporting_quotes: list[str] = Field(default_factory=list)
    uplift_opportunity: Optional[str] = None
    score: Optional[PainPointScore] = None

class AdditionalPainPoint(BaseModel):
    description: str
    supporting_quotes: list[str]
    suggested_lv3_alignment: Optional[str] = None
    uplift_opportunity: Optional[str] = None

class Lv3Analysis(BaseModel):
    lv3_id: str
    lv3_name: str
    lv3_description: str
    lv3_score: RAGScore
    lv3_score_reason: Optional[str] = None
    pain_points: list[PainPoint]

class Metadata(BaseModel):
    lv1_area: str
    lv2_area: str
    analysis_date: date
    confidence: Confidence

class Summary(BaseModel):
    lv2_score: RAGScore
    lv2_score_reason: str
    key_pain_points: list[str]
    key_uplift_opportunity: str
    total_pain_points_observed: int = 0
    total_additional_pain_points: int = 0

class PainPointAnalysisOutput(BaseModel):
    """Structured output from the client pain point analysis workflow"""
    metadata: Metadata
    summary: Summary
    analysis: list[Lv3Analysis]
    additional_pain_points: list[AdditionalPainPoint] = Field(default_factory=list)
```

---

## Example Output

```json
{
  "metadata": {
    "lv1_area": "05.00 Source to Pay",
    "lv2_area": "05.10 Purchasing/Payment Inquiries",
    "analysis_date": "2026-04-21",
    "confidence": "High"
  },
  "summary": {
    "lv2_score": "Significant Challenges",
    "lv2_score_reason": "Multiple pain points observed with high urgency and frequency",
    "key_pain_points": [
      "No supplier self-service portal",
      "Limited buyer self-service for requisition inquiries"
    ],
    "key_uplift_opportunity": "Implement supplier self-service portal with integrated inquiry management",
    "total_pain_points_observed": 4,
    "total_additional_pain_points": 1
  },
  "analysis": [
    {
      "lv3_id": "05.10.01",
      "lv3_name": "Manage Supplier Self-Service Portal",
      "lv3_description": "The process for maintaining the supplier self-service portal and the information stored on it.",
      "lv3_score": "Significant Challenges",
      "lv3_score_reason": "Core pain point observed with high frequency",
      "pain_points": [
        {
          "pain_point_id": "1",
          "framework_pain_point": "There is currently no supplier self-service portal",
          "observed": true,
          "client_specific_expression": "We don't have any way for suppliers to check their own status",
          "supporting_quotes": [
            "Our suppliers are constantly calling us to check on invoice status",
            "We get dozens of emails a day from vendors asking about payments"
          ],
          "uplift_opportunity": "Implement a supplier portal with real-time invoice and payment status visibility",
          "score": {
            "relevance": "High",
            "urgency": "High",
            "frequency": "High",
            "opportunity": "High",
            "overall": "High"
          }
        }
      ]
    }
  ],
  "additional_pain_points": [
    {
      "description": "Manual reconciliation between Prism and Nexus systems",
      "supporting_quotes": [
        "We spend hours every week reconciling data between the two systems"
      ],
      "suggested_lv3_alignment": "05.10.04 Manage Payment Inquiries & Exceptions",
      "uplift_opportunity": "Automated reconciliation workflow between systems"
    }
  ]
}
```

---

## Usage in Formatter Agent

The Formatter agent should use this schema as its `output_type`:

```python
formatter = Agent(
    name="Formatter",
    instructions="...",
    output_type=PainPointAnalysisOutput
)
```

This ensures the SDK enforces schema compliance at the output level.
