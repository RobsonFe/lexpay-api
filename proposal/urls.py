from django.urls import path
from proposal.views import CreateProposalView, ProposalListView, ProposalDeleteView, ProposalUpdateView, ProposalAcceptView, InvestorOpportunitiesView

urlpatterns = [
    path ("create/", CreateProposalView.as_view(), name="create_proposal"),
    path("list/", ProposalListView.as_view(), name="list_proposals"),
    path("update/<uuid:pk>/", ProposalUpdateView.as_view(), name="update_proposal"),
    path("delete/<uuid:pk>/", ProposalDeleteView.as_view(), name="delete_proposal"),
    path("accept/<uuid:pk>/", ProposalAcceptView.as_view(), name="accept_proposal"),
    path("opportunities/", InvestorOpportunitiesView.as_view(), name="investor_opportunities"),
]
