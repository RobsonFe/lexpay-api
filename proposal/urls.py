from django.urls import path
from proposal.views import CreateProposalView, ProposalListView

urlpatterns = [
    path ("create/", CreateProposalView.as_view(), name="create_proposal"),
    path("list/", ProposalListView.as_view(), name="list_proposals"),
]
