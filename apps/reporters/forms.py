from django import forms
class UploadImportFileForm(forms.Form):
	
	import_file = forms.FileField(label='Select your XLS file:')
