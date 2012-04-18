from django import forms
from django.forms import widgets
from models import Annotation, Target, Constraint
from django.utils import simplejson
from django.utils.simplejson import JSONDecodeError

TargetFormSet = forms.models.inlineformset_factory(Target, Annotation.target.through)

class TestForm(forms.Form):
    data = forms.CharField(required=True, widget=widgets.Textarea())

    def clean_data(self):
        try:
            return simplejson.loads(self.cleaned_data['data'])
        except JSONDecodeError:
            return self.cleaned_data['data']

class ModelGetOrCreateMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, queryset, field_name='', **kwargs):
        super(forms.ModelMultipleChoiceField, self).__init__(queryset, **kwargs)
        if not field_name:
            raise Exception('You should to pass field name into field constructor.')
        self.field_name = field_name

    def clean(self, value):
        Model = self.queryset.model
        qs = None

        if self.required and not value:
            raise forms.ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        '''
        BE CAREFULL!!!
        HERE IS MAY BE A BUG!
        '''
        if isinstance(value, dict):
            value = (value,)
        '''
        DELETE previous 2 lines if XML doesn't works fine. 
        '''
        if not isinstance(value, (list, tuple)):
            raise forms.ValidationError(self.error_messages['list'])


        if all(isinstance(i, dict) for i in value):
            values = [i[self.field_name] for i in value]

            # if all values are already in DB
            if len(value) <= Model.objects.filter(**{self.field_name+"__in": values}).count():
                qs = Model.objects.filter(**{self.field_name+"__in": values})

            elif all([isinstance(i, basestring) for i in values]):
                qs = Model.objects.filter(pk__in=[
                    Model.objects.get_or_create(**{self.field_name: i})[0].pk
                    for i in values
                ])
            else:
                raise forms.ValidationError(self.error_messages['invalid_choice'] % values)

            return qs
        return super(ModelGetOrCreateMultipleChoiceField, self).clean(value)



class AnnotationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', '')
        target_kw = dict(
            queryset=Target.objects.all(), field_name='url', required=True,
        )
        if instance:
            init = Target.objects.filter(url__in=list(instance.target.all()))
            target_kw.update({'initial': init})
        target = ModelGetOrCreateMultipleChoiceField(**target_kw)
        self.base_fields['target'] = target

        super(AnnotationForm, self).__init__(*args, **kwargs)

    id = forms.IntegerField(required=False)
    target = ModelGetOrCreateMultipleChoiceField(
        queryset=Target.objects.all(), field_name='url', required=True,
        initial=Target.objects.filter()
    )

    def save(self, commit=True):
        instance = super(AnnotationForm, self).save(commit)

        #if commit:
        #    print "COMMIT TRUE"
        #    qs = Annotation.objects.filter(
        #        target__url__in=[t for t in instance.target.all()],
        #        has_answers=False,
        #        deleted=False
        #    )
        #    if self.instance.type.lower() == "reply" and qs.count():
        #        from handlers import log
        #        log.info("form save qs count {0}".format(qs.count()))
        #        qs.update(has_answers=True)
        return instance

    class Meta:
        model = Annotation
        exclude = ('author', 'creation_date', 'modification_date',
                   'deleted', 'deleted_at', 'has_answers'
                  )



class ConstraintForm(forms.ModelForm):
    """This form validates constraints"""

    class Meta:
        model = Constraint
        exclude = ('target', 'annotation',)

