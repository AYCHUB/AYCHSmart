# coding: utf-8
"""
Utils for pydici action set module
@author: Sébastien Renard (sebastien.renard@digitalfox.org)
@license: AGPL v3 or newer (http://www.gnu.org/licenses/agpl-3.0.html)
"""

from pydici.actionset.models import ActionSet

def launchTrigger(trigger, targetUsers, targetObject=None):
    """Launch actionset about targetObject for given trigger to targeted users"""
    if not trigger in ActionSet.ACTIONSET_TRIGGERS:
        raise Exception(_("Trigger %s is not defined" % trigger))

    for actionSet in ActionSet.objects.filter(trigger=trigger):
        for user in targetUsers:
            actionSet.start(user, targetObject)
