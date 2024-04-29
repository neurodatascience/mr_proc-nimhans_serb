"""Class for bagel tracker files."""

from typing import Optional

from pydantic import field_validator, model_validator

from nipoppy.tabular.base import BaseTabular, BaseTabularModel
from nipoppy.utils import participant_id_to_bids_id

STATUS_SUCCESS = "SUCCESS"
STATUS_FAIL = "FAIL"
STATUS_INCOMPLETE = "INCOMPLETE"
STATUS_UNAVAILABLE = "UNAVAILABLE"


class BagelModel(BaseTabularModel):
    """Model for the bagel file."""

    participant_id: str
    bids_id: Optional[str] = None
    session: str
    pipeline_name: str
    pipeline_version: str
    pipeline_complete: str

    @field_validator("pipeline_complete")
    @classmethod
    def check_status(cls, value: str):
        """Check that a status field has a valid value."""
        valid_statuses = [
            STATUS_SUCCESS,
            STATUS_FAIL,
            STATUS_INCOMPLETE,
            STATUS_UNAVAILABLE,
        ]
        if value not in valid_statuses:
            raise ValueError(
                f"Invalid status '{value}'. Must be one of: {valid_statuses}."
            )
        return value

    @model_validator(mode="after")
    def check_bids_id(self):
        """Generate default value for optional BIDS ID field."""
        if self.bids_id is None:
            self.bids_id = participant_id_to_bids_id(self.participant_id)


class Bagel(BaseTabular):
    """A file to track data availability/processing status."""

    # column names
    col_participant_id = "participant_id"
    col_bids_id = "bids_id"
    col_session = "session"
    col_pipeline_name = "pipeline_name"
    col_pipeline_version = "pipeline_version"
    col_pipeline_complete = "pipeline_complete"

    # pipeline statuses
    status_success = STATUS_SUCCESS
    status_fail = STATUS_FAIL
    status_incomplete = STATUS_INCOMPLETE
    status_unavailable = STATUS_UNAVAILABLE

    # for sorting/comparing between bagels
    index_cols = [
        col_participant_id,
        col_bids_id,
        col_session,
        col_pipeline_name,
        col_pipeline_version,
    ]

    _metadata = BaseTabular._metadata + [
        "col_participant_id",
        "col_bids_id",
        "col_session",
        "col_pipeline_name",
        "col_pipeline_version",
        "col_pipeline_complete",
        "status_success",
        "status_fail",
        "status_incomplete",
        "status_unavailable",
        "index_cols",
    ]

    # set the model
    model = BagelModel
