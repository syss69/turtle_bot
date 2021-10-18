import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials


class GoogleTables:
    def __init__(self, tableId: str) -> None:
        self.spreadsheetId = tableId
        CREDENTIALS_FILE = 'newagent-gkwucb-3a47047b957e.json'  # имя файла с закрытым ключом

        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                       ['https://www.googleapis.com/auth/spreadsheets',
                                                                        'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        self.service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth, cache_discovery=False)

    def take_values_table(self):
        ranges = ["Лист1!A1:C10000"]
        results = self.service.spreadsheets().values().batchGet(spreadsheetId=self.spreadsheetId,
                                                                ranges=ranges,
                                                                valueRenderOption='FORMATTED_VALUE',
                                                                dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        return sheet_values




