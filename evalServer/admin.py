from django.contrib import admin
from evalServer.models import MatrixItem, IntegrityCheck, MatrixAnswer

class MatrixItemAdmin(admin.ModelAdmin):
	list_display = ('fileID', 'name', 'email')

class MatrixAnswerAdmin(admin.ModelAdmin):
	list_display = ('matrixItem', 'userName', 'timeTaken')

class IntegrityCheckAdmin(admin.ModelAdmin):
	list_display = ('matrixItem', 'rater', 'correct')

admin.site.register(MatrixItem, MatrixItemAdmin)
admin.site.register(MatrixAnswer, MatrixAnswerAdmin)
admin.site.register(IntegrityCheck, IntegrityCheckAdmin)
