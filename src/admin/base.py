from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class DevSuiteAdminSite(AdminSite):
    site_header = "DevSuite Admin"
    site_title = "DevSuite Admin Portal"
    index_title = "Welcome to DevSuite Administration"

    def get_app_list(self, request, app_label=None):
        """
        Override to organize models into logical groups.
        """
        app_list = super().get_app_list(request, app_label)

        model_map = {
            # Clients
            "Client": {
                "group": "Clients",
                "display_name": "Clients",
                "order": 1,
            },
            # Finance
            "Invoice": {
                "group": "Finance",
                "display_name": "Invoices",
                "order": 1,
            },
            "Expense": {
                "group": "Finance",
                "display_name": "Expenses",
                "order": 2,
            },
            "Payment": {
                "group": "Finance",
                "display_name": "Payments",
                "order": 3,
            },
            # Productivity
            "Note": {
                "group": "Productivity",
                "display_name": "Notes",
                "order": 1,
            },
            "TimeEntry": {
                "group": "Productivity",
                "display_name": "Time Entries",
                "order": 2,
            },
            # Projects
            "Project": {
                "group": "Projects",
                "display_name": "Projects",
                "order": 1,
            },
            "Milestone": {
                "group": "Projects",
                "display_name": "Milestones",
                "order": 2,
            },
            "Task": {
                "group": "Projects",
                "display_name": "Tasks",
                "order": 3,
            },
            # Services
            "Service": {
                "group": "Services",
                "display_name": "Services",
                "order": 1,
            },
            "Credential": {
                "group": "Services",
                "display_name": "Credentials",
                "order": 2,
            },
            # System & Users
            "User": {
                "group": "System & Users",
                "display_name": "Admin Users",
                "order": 1,
            },
            "Group": {
                "group": "System & Users",
                "display_name": "Groups",
                "order": 2,
            },
            "Notification": {
                "group": "System & Users",
                "display_name": "Notifications",
                "order": 3,
            },
        }

        # Group models according to the model_map
        grouped_models = {}
        for app in app_list:
            for model in app["models"]:
                model_name = model["object_name"]
                if model_name in model_map:
                    config = model_map[model_name]
                    group = config["group"]

                    if group not in grouped_models:
                        grouped_models[group] = {
                            "name": group,
                            "app_label": group.lower()
                            .replace(" ", "_")
                            .replace("&", "and"),
                            "models": [],
                        }

                    # Use custom display name
                    model["name"] = config["display_name"]
                    model["_order"] = config["order"]
                    grouped_models[group]["models"].append(model)

        # Sort models within each group by their order
        for group_dict in grouped_models.values():
            group_dict["models"].sort(key=lambda m: m.get("_order", 999))

        # Define the order of groups (most frequently accessed first)
        group_order = [
            "Clients",
            "Projects",
            "Services",
            "Finance",
            "Productivity",
            "System & Users",
        ]

        # Build final app list in the defined order
        grouped_app_list = [
            grouped_models[g] for g in group_order if g in grouped_models
        ]

        return grouped_app_list


admin_site = DevSuiteAdminSite(name="ssgd_admin")
admin_site.register(User, UserAdmin)
