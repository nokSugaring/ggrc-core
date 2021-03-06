# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Contains the Assignable mixin.

This allows adding various assignee types to the object, like Verifiers,
Creators, etc.
"""

from collections import defaultdict

from ggrc.access_control.roleable import Roleable


class Assignable(Roleable):
  """Mixin for models with assignees"""

  ASSIGNEE_TYPES = {"Creators", "Assignees", "Verifiers"}

  @property
  def assignees(self):
    """Returns assignees.

    Returns:
        A dict of assignees and their roles.
    """
    assignees = defaultdict(list)
    for person, acl in self.access_control_list:
      if acl.ac_role.name in self.ASSIGNEE_TYPES:
        assignees[person].append(acl.ac_role.name)

    return assignees

  @property
  def verifiers(self):
    """Returns verifiers.

    Returns:
        A list of Verifiers.
    """
    return [person for person, acl in self.access_control_list
            if acl.ac_role.name == "Verifiers"]
