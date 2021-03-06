"""
Test to create and verify the state of the group.
"""
from test_repo.autoscale.fixtures import AutoscaleFixture


class GetListEntityStatusTest(AutoscaleFixture):

    """
    Verify list group state.
    """

    @classmethod
    def setUpClass(cls):
        """
        Create a scaling group.
        """
        super(GetListEntityStatusTest, cls).setUpClass()
        cls.gc_max_entities = 10
        group_response = cls.autoscale_behaviors.create_scaling_group_given(
            gc_min_entities=cls.gc_min_entities_alt,
            gc_max_entities=cls.gc_max_entities)
        cls.group = group_response.entity
        cls.group_state_response = cls.autoscale_client.list_status_entities_sgroups(
            cls.group.id)
        cls.group_state = cls.group_state_response.entity

    def test_entity_status_response(self):
        """
        Verify list status' response code is 200, header.
        """
        self.assertEquals(200, self.group_state_response.status_code,
                          msg='The list entities call failed with {0} for group '
                          '{1}'.format(self.group_state_response.status_code, self.group.id))
        self.validate_headers(self.group_state_response.headers)

    def test_entity_status(self):
        """
        Verify list status' data.
        """
        self.assertEquals(
            self.group_state.name, self.group.groupConfiguration.name,
            msg='The group name does not match in group'
            ' state for group {0}'.format(self.group.id))
        self.assert_group_state(self.group_state)
        self.assertGreaterEqual(
            self.group_state.desiredCapacity, self.gc_min_entities_alt,
            msg='Less than required number of servers in desired capacity'
            ' for group {0}'.format(self.group.id))
        self.assertLessEqual(
            self.group_state.desiredCapacity, self.gc_max_entities,
            msg='Total server count is over maxEntities'
            ' for group {0}'.format(self.group.id))
        self.empty_scaling_group(self.group)
