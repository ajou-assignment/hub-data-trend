from django.contrib import admin
from repos.models import Organization, Repository, Branch, Commit


admin.site.register(Organization)
admin.site.register(Repository)
admin.site.register(Branch)
admin.site.register(Commit)
