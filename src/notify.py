import mmap, os, re, sys
from PyObjCTools import AppHelper
import Foundation
import objc
import AppKit

import time
from threading import Timer
from datetime import datetime, date

class Notification(Foundation.NSObject):
    def __init__(self):
        self = super(Notification, self).init()
        if self is None: return None

        # Get objc references to the classes we need.
        self.NSUserNotification = objc.lookUpClass('NSUserNotification')
        self.NSUserNotificationCenter = objc.lookUpClass('NSUserNoticicationCenter')

    def clearNotifications(self):
        """Clear any displayed alerts we have posted."""

        NSUserNotificationCenter = objc.lookUpClass('NSUserNotificationCenter')
        NSUserNotificationCenter.defaultUserNotificationCenter().removeAllDeliveredNotifications()

    def notify(self, title: str, subtitle: str, text: str, url: str):
        """Create a user notification and display it."""

        notification = self.NSUserNotification.alloc().init()
        notification.setTitle_(title)
        notification.setSubtitle_(subtitle)
        notification.setInformativeText_(text)
        notification.setSoundName_('NSUSerNotificationDefaultSoundName')
        notification.setHasActionButton_(True)
        notification.setActionButtonTitle_("View")
        notification.setUserInfo_({'action': 'open_url', 'value': url})

        self.NSUserNoticicationCenter.defaultUserNotificationCenter().setDelegate_(self)
        self.NSUserNoticicationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)

        return notification

    def userNotificationCenter_didActivateNotification_(self, center, notification):
        """Handler for clicking on a posted notification."""

        userInfo = notification.userInfo()
        if userInfo['action'] == 'open_url':
            import subprocess
            # Open the log file with TextEdit
            subprocess.Popen(['open', '-e', userInfo['value']])













# import Foundation
# import objc
# import AppKit
# import sys

# NSUserNotification = objc.lookUpClass('NSUserNotification')
# NSUserNotificationCenter = objc.lookUpClass('NSUserNotificationCenter')

# def notify(title, subtitle, info_text, delay=0, sound=False, userInfo={}):
#     notification = NSUserNotification.alloc().init()
#     notification.setTitle_(title)
#     notification.setSubtitle_(subtitle)
#     notification.setInformativeText_(info_text)
#     notification.setUserInfo_(userInfo)

#     if sound:
#         notification.setSoundName_("NSUserNotificationDefaultSoundName")
#     notification.setDeliveryDate_(Foundation.NSDate.dateWithTimeInterval_sinceDate_(delay, Foundation.NSDate.date()))
#     NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)

if __name__ == '__main__':
    # notify('Test Message', 'My Subtitle', 'This message should appear instantly, with a sound', sound=True)
    # sys.stdout.write('Notification sent...\n')
    n = Notification()
    n.clearNotifications()

