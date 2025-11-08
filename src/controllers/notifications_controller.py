from models.announcement import Announcement
from bson.objectid import ObjectId


class NotificationsController:
    def __init__(self):
        self.announcement_model = Announcement("", "", "")

    def admin_post_announcement(self, title, content, admin_id):
        """
        Admin tạo và đăng (publish) một thông báo ngay lập tức
        """
        try:
            new_ann = Announcement(
                title=title, content=content, createBy=ObjectId(admin_id)
            )

            # Chuyển status sang published và lưu thông báo này
            new_ann.publish()

            # Trả về message
            return {
                "success": True,
                "message": "Posted an announcement successfully",
            }
        except Exception as e:
            print(e)
            return {"success": False, "message": "Failed to post an announcement"}

    def student_view_all_notifications(self):
        """
        Sinh viên xem toàn bộ thông báo mà Admin đã tạo và đăng lên
        """
        return self.announcement_model.find_all()


# a = NotificationsController()
# print(a.admin_post_announcement("test", "I just want to test the controller", "01"))
# print(a.student_view_all_notifications())
