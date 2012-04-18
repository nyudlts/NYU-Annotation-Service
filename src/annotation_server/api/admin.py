from django.contrib import admin
from models import *
from forms import AnnotationForm

class TargetAdmin(admin.ModelAdmin):
    pass

class TargetAnnotation(admin.TabularInline):
    extra = 1
    model = Annotation.target.through

def targets(instance):
    return ", ".join(i.url for i in instance.target.all())

class AnnotationAdmin(admin.ModelAdmin):
    #form = AnnotationForm
    ordering = ('-creation_date',)
    list_display = ('type', 'body', 'author', 'creation_date',
                    'modification_date', 'deleted', 'get_absolute_url',
                    'has_answers', 'was_changed', targets, 'private')
    list_filter = ('creation_date', 'deleted', 'modification_date', 'author')
    date_hierarchy = 'creation_date'
    inlines = [ TargetAnnotation, ]

    exclude = ('target',)


admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Target, TargetAdmin)
admin.site.register((Constraint, Profile))
#admin.site.register((Book,))
