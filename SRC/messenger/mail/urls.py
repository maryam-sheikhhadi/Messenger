from django.urls import path
from .views import *


urlpatterns = [
    #email urls: create, list, detail, reply, forward, delete, edite
    path('create-email', CreateEmail.as_view(), name="create-email"),
    path('all-mails', EmailList.as_view(), name="all-mails"),
    path('mail-detail/<int:pk>', EmailDetail.as_view(), name="mail-detail"),
    path('reply-email/<int:pk>', ReplyEmail.as_view(), name="reply-email"),
    path('forward-email/<int:pk>', ForwardEmail.as_view(), name="forward-email"),
    path('send-from-draft/<int:pk>', SendDraft.as_view(), name="send-from-draft"),
    path('delete-email/<int:pk>', DeleteEmail.as_view(), name='delete-email'),
    path('edit_email/<int:pk>', UpdateEmail.as_view(), name='edit_email'),
    #label urls: create, list, detail with slug, delete, search
    path('create-label', CreateLabel.as_view(), name="create-label"),
    path('labels', LabelList.as_view(), name="labels"),
    path('labels/<slug:slug>', LabelDetail.as_view(), name="label-detail"),
    path('delete-label/<slug:slug>', DeleteLabel.as_view(), name='delete-label'),
    path('search-label', SearchByLable.as_view(), name='search-label'),
    path('add-label/<int:pk>', AddLabel.as_view(), name='add-label'),
    #categories: sent, inbox, draft, archive, trash
    path('sent_box', SentBox.as_view(), name='sent_box'),
    path('inbox', Inbox.as_view(), name='inbox'),
    path('draft', Draft.as_view(), name='draft'),
    path('archive', Archive.as_view(), name='archive'),
    path('trash', Trash.as_view(), name='trash'),
    #signature
    path('create-signature', CreateSignature.as_view(), name='create-signature'),
    path('signature-detail/<int:pk>', SignatureDetail.as_view(), name='signature-detail'),
    path('signatures', SignatureList.as_view(), name='signatures'),
]