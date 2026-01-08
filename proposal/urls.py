from django.urls import path
from proposal.views import CreateProposalView, ProposalListView, ProposalDeleteView, ProposalUpdateView

urlpatterns = [
    path ("create/", CreateProposalView.as_view(), name="create_proposal"),
    path("list/", ProposalListView.as_view(), name="list_proposals"),
    path("update/<int:pk>/", ProposalUpdateView.as_view(), name="update_proposal"),
    path("delete/<int:pk>/", ProposalDeleteView.as_view(), name="delete_proposal"),
]
