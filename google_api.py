from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service.json'

creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

def _read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')
    if not text_run:
        return ''
    return text_run.get('content')

def _read_structural_elements(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """
    text = ''
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text += _read_paragraph_element(elem)
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be nested.
            table = value.get('table')
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    text += _read_structural_elements(cell.get('content'))
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += _read_structural_elements(toc.get('content'))
    return text

def get_raw_text_from_doc(doc_id):
    service = build('docs', 'v1', credentials=creds)
    document = service.documents().get(documentId=doc_id).execute()
    doc_content = document.get('body').get('content')
    return _read_structural_elements(doc_content)

def execute_folder_query(service, query):
    resp = service.files().list(q=query).execute()
    files = resp.get('files')
    return files

def execute_get_query(service, id, field):
    resp = service.files().get(fileId=id, fields=field).execute()
    return resp.get(field)

def iterate_content_folder(folder_id):
    service = build('drive', 'v3', credentials=creds)
    subfolders = execute_folder_query(service, f"parents = '{folder_id}'")
    res = dict()
    for fs in subfolders:
        if 'folder' in fs['mimeType'] and 'Chapter' in fs['name']:
            res[fs['name']] = []
            subfiles = execute_folder_query(service, f"parents = '{fs['id']}'")
            for file in subfiles:
                if 'folder' not in file['mimeType']:
                    link = execute_get_query(service, file['id'], 'webViewLink')
                    res[fs['name']].append((file['name'], link))
    return sorted(res.items(), key=lambda x: x[0])


def main():
    from dotenv import load_dotenv
    load_dotenv()
    import os
    QUESTION_DOC = os.getenv('QUESTION_DOC_ID')
    folder_id = '1-hWNixXLRrfLVWDawWNmv34MWjNOvDkm'

    # print(get_raw_text_from_doc(QUESTION_DOC))
    res = iterate_content_folder(folder_id)
    for key, val in res:
        print(key)
        for v in val:
            print('\t'+v[0], v[1])
    # service = build('drive', 'v3', credentials=creds)
    # print(execute_get_query(service, '13gHBCt6gi74gtHIN0qSB2ee0iJ3RBRu6oB_b7WzuKRI', 'webViewLink'))

if __name__ == '__main__':
    main()