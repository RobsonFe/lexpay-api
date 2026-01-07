
'''from rest_framework import serializers
from proposal.models import Proposal, ProposalHistory


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'update_at')

class ProposalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalHistory
        fields = '__all__'
        read_only_fields = ('id', 'created_at')
        '''