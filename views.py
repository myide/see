from sqlmng.models import Inceptsql
from .mixins import DownloadBaseView

# Create your views here.
class SqlFileView(DownloadBaseView):
    '''
        文件下载
    '''
    model = Inceptsql

    def get_content(self):
        pk = self.kwargs.get('pk')
        data_type = self.request.GET.get('data_type')
        instance = self.model.objects.get(pk=pk)
        content = getattr(instance, data_type)
        return content
