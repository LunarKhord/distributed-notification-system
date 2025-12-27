from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from typing import Optional

# API Specification Overview
"""
POST /api/v1/notifications/

Operationalizes the dispatch of multi-channel communications by ingesting 
a structured payload. This endpoint serves as the ingress point for 
asynchronous or synchronous notification delivery.
"""

class NotificationType(str, Enum):
    """
    An enumeration serving as a restricted vocabulary to define the 
    communication modalities supported by the notification engine.
    """
    email = "email"
    push = "push"
    sms = "sms"


class UserData(BaseModel):
    """
    A data transfer object (DTO) encapsulated within a Pydantic model 
    to facilitate rigorous validation of recipient-specific variables.
    """
    name: str = Field(..., description="The moniker of the intended recipient")
    link: HttpUrl = Field(..., description="A syntactically valid URL for resource redirection")
    meta: Optional[dict] = Field(..., description="Ancillary key-value pairs for heterogeneous data inclusion")


class Notification(BaseModel):
    """
    The quintessential schema definition for a notification request. 
    It enforces type safety and structural integrity for the primary 
    payload, ensuring that all requisite attributes are present 
    prior to downstream processing.
    """
    # Categorizes the transmission medium
    notification_type: NotificationType = Field(..., description="The designated medium for dissemination")
    
    # Identifies the target entity
    user_id: str = Field(..., description="The universally unique identifier (UUID) of the recipient")
    
    # Specifies the aesthetic and structural blueprint
    template_code: str = Field(..., description="The symbolic identifier for the content boilerplate")
    
    # Injects dynamic content into the template
    variables: UserData = Field(..., description="Interpolation parameters for template hydration")
    
    # Facilitates idempotency and traceability
    request_id: str = Field(..., description="A unique token for transactional auditing and logging")
    
    # Determines the urgency of the dispatch
    priority: int = Field(..., description="A numerical value denoting the exigency of the message")
    
    # Optional contextual data
    metadata: Optional[dict] = Field(None, description="Supplementary contextual attributes for downstream consumers")