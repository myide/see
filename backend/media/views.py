from sqlmng.models import Inceptsql
from .mixins import DownloadBaseView

# Create your views here.
class SqlFileView(DownloadBaseView):
    model = Inceptsql
    def get_content(self):
        pk = self.kwargs.get('pk')
        content = self.model.objects.get(pk=pk).handle_result
        return content
