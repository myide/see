from sqlmng.models import Inceptsql
from .mixins import DownloadBaseView

# Create your views here.
class SqlFileView(DownloadBaseView):
    
    model = Inceptsql
    
    def get_content(self):
        '''
            文件下载
        '''
        pk = self.kwargs.get('pk')
        content = self.model.objects.get(pk=pk).handle_result
        return content
