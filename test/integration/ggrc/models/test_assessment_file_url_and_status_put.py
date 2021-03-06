# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Integration tests for Assessment action and status change."""
import ddt

from ggrc.models import all_models

from integration import ggrc
from integration.ggrc.models import factories


@ddt.ddt
class TestAssessmentCompleteWithAction(ggrc.TestCase):
  """Test Assessment complete status with action."""
  def setUp(self):
    """Set up audit and cad for test cases."""
    super(TestAssessmentCompleteWithAction, self).setUp()
    self.api = ggrc.api_helper.Api()
    with factories.single_commit():
      self.audit = factories.AuditFactory()
      self.asmt = factories.AssessmentFactory(audit=self.audit,
                                              status="In Progress")
      self.evidence = factories.EvidenceFactory()

  def _prepare_mandatory_evidence_cad(self):
    """Prepare mandatory evidence"""
    cad = factories.CustomAttributeDefinitionFactory(
        attribute_type="Dropdown",
        definition_type="assessment",
        definition_id=self.asmt.id,
        multi_choice_options="value_1,value_2",
        multi_choice_mandatory="0,2",
    )
    factories.CustomAttributeValueFactory(
        custom_attribute=cad,
        attributable=self.asmt,
        attribute_value="value_2",
    )

  @ddt.data(("In Review", "In Review"),
            ("Verified", "Completed"),
            ("Completed", "Completed"),
            ("Deprecated", "Deprecated"))
  @ddt.unpack
  def test_add_evidence_and_status(self, status, result_status):
    """Test add evidence and update {0} status to {1}
    in single PUT."""
    asmt_id = self.asmt.id

    # putting assessment to 'In Progress' state
    self.api.put(self.asmt, {
        "actions": {"add_related": [{"id": self.evidence.id,
                                     "type": "Evidence"}]},
    })
    new_evidence = factories.EvidenceFactory()
    response = self.api.put(self.asmt, {
        "status": status,
        "actions": {"add_related": [{"id": new_evidence.id,
                                     "type": "Evidence"}]},
    })
    self.assertEqual(response.status_code, 200)
    response_asmt = response.json["assessment"]
    self.assertEqual(response_asmt["status"], result_status)

    asmt = all_models.Assessment.query.get(asmt_id)
    self.assertEqual(asmt.status, result_status)

  @ddt.data(("In Review", "In Review"),
            ("Verified", "Completed"),
            ("Completed", "Completed"),
            ("Deprecated", "Deprecated"))
  @ddt.unpack
  def test_remove_evidence_and_status(self, status, result_status):
    """Test remove evidence and update {0} status to {1}
    in single PUT."""
    asmt_id = self.asmt.id

    # putting assessment to 'In Progress' state
    self.api.put(self.asmt, {
        "actions": {"add_related": [{"id": self.evidence.id,
                                     "type": "Evidence"}]},
    })
    response = self.api.put(self.asmt, {
        "status": status,
        "actions": {"remove_related": [{"id": self.evidence.id,
                                        "type": "Evidence"}]},
    })
    self.assertEqual(response.status_code, 200)
    response_asmt = response.json["assessment"]
    self.assertEqual(response_asmt["status"], result_status)

    asmt = all_models.Assessment.query.get(asmt_id)
    self.assertEqual(asmt.status, result_status)

  @ddt.data("In Review", "Verified", "Completed")
  def test_remove_required_evidence(self, status):
    """Test remove mandatory evidence and update
    status to {0} in single PUT. Result status
    should be `In Progress`"""
    asmt_id = self.asmt.id
    self._prepare_mandatory_evidence_cad()
    rel = factories.RelationshipFactory(
        source=self.asmt,
        destination=self.evidence,
    )
    rel_id = rel.id
    response = self.api.put(self.asmt, {
        "status": status,
        "actions": {"remove_related": [{"id": self.evidence.id,
                                        "type": "Evidence"}]},
    })
    self.assertEqual(response.status_code, 400)
    message = response.json["message"]
    self.assertEqual(message, "CA-introduced completion preconditions "
                              "are not satisfied. Check preconditions_failed"
                              " of items of self.custom_attribute_values")
    asmnt = all_models.Assessment.query.filter_by(id=asmt_id).first()
    self.assertEqual(asmnt.status, "In Progress")

    relationship = all_models.Relationship.query.get(rel_id)
    self.assertIsNotNone(relationship)

  def test_remove_req_evid_deprecated(self):
    """Test remove mandatory evidence and update
    status to deprecated in single PUT. Result status
    should be `Deprecated`"""
    asmt_id = self.asmt.id
    self._prepare_mandatory_evidence_cad()
    rel = factories.RelationshipFactory(
        source=self.asmt,
        destination=self.evidence,
    )
    rel_id = rel.id
    response = self.api.put(self.asmt, {
        "status": "Deprecated",
        "actions": {"remove_related": [{"id": self.evidence.id,
                                        "type": "Evidence"}]},
    })
    self.assertEqual(response.status_code, 200)
    asmnt = all_models.Assessment.query.filter_by(id=asmt_id).first()
    self.assertEqual(asmnt.status, "Deprecated")

    relationship = all_models.Relationship.query.get(rel_id)
    self.assertIsNone(relationship)

  def test_remove_req_evid_progress(self):
    """Test remove mandatory evidence and update
    status to deprecated in single PUT. Result status
    should be `In Progress`"""
    asmt_id = self.asmt.id
    self._prepare_mandatory_evidence_cad()
    rel = factories.RelationshipFactory(
        source=self.asmt,
        destination=self.evidence,
    )
    rel_id = rel.id
    response = self.api.put(self.asmt, {
        "status": "In Progress",
        "actions": {"remove_related": [{"id": self.evidence.id,
                                        "type": "Evidence"}]},
    })
    self.assertEqual(response.status_code, 200)
    asmnt = all_models.Assessment.query.filter_by(id=asmt_id).first()
    self.assertEqual(asmnt.status, "In Progress")

    relationship = all_models.Relationship.query.get(rel_id)
    self.assertIsNone(relationship)
