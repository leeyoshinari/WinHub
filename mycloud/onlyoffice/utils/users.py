"""

 (c) Copyright Ascensio System SIA 2024

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

"""


class User:
    def __init__(self, uid, name, email, group, reviewGroups, commentGroups, userInfoGroups, favorite,
                 deniedPermissions, descriptions, templates, avatar):
        self.id = uid
        self.name = name
        self.email = email
        self.group = group
        self.reviewGroups = reviewGroups
        self.commentGroups = commentGroups
        self.favorite = favorite
        self.deniedPermissions = deniedPermissions
        self.descriptions = descriptions
        self.templates = templates
        self.userInfoGroups = userInfoGroups
        self.avatar = avatar


def getUser(user_id, user_name):
    return User(user_id, user_name, None, 'group1', ['group1'], {'view': ["group1"], 'edit': ["group1"],  'remove': ["group1"]},
                ['group1'], None, [], "Default", True, True)
