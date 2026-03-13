import threading
import uuid
from decimal import Decimal
from datetime import date
from django.test import TransactionTestCase
from django.db import connection
from django.contrib.auth import get_user_model
from django.utils import timezone
from oficio.models import Precatorio, StatusPrecatorioChoices, Tribunal, EnteDevedor, NaturezaChoices
from proposal.models import Proposal, StausChoices
from proposal.services import ProposalService

User = get_user_model()

class ProposalConcurrencyTest(TransactionTestCase):
    def setUp(self):
        # 1. Criar Usuários (Dono e Proponente)
        self.cedente = User.objects.create_user(username="cedente", type_user="Cedente", email="cedente@example.com", password="testpass123")
        self.broker = User.objects.create_user(username="broker_test", type_user="Broker", email="broker@example.com", password="testpass123")

        # 2. Criar Dependências do Precatório
        self.tribunal = Tribunal.objects.create(nome="TJSP")
        self.ente = EnteDevedor.objects.create(nome="Prefeitura")

        # 3. Criar Precatório (Note o valor_principal e percentual_honorarios para o save da Proposal)
        self.precatorio = Precatorio.objects.create(
            cedente=self.cedente,
            tribunal=self.tribunal,
            ente_devedor=self.ente,
            numero_processo=str(uuid.uuid4()),
            natureza=NaturezaChoices.ALIMENTAR,
            valor_principal=Decimal("100000.00"),
            percentual_honorarios=Decimal("10.00"),
            data_expedicao=date(2023, 1, 1),
            ano_orcamentario=2024,
            status=StatusPrecatorioChoices.DISPONIVEL
        )

        # 4. Dados padrão para as Propostas (Para satisfazer o método save())
        self.common_params = {
            "precatorio": self.precatorio,
            "proponente": self.broker,
            "taxa_desconto": Decimal("15.00"),
            "taxa_juros_anual": Decimal("12.00"),
            "prazo_pagamento_meses": 12,
            "data_vencimento": timezone.now().date() + timezone.timedelta(days=7),
        }

        # 5. Criar Proposta Alvo (status ENVIADA conforme seu Service espera)
        self.proposal = Proposal.objects.create(
            valor_proposto=Decimal("80000.00"),
            status=StausChoices.ENVIADA,
            **self.common_params
        )

        # 6. Criar Proposta Concorrente
        self.concorrente = Proposal.objects.create(
            valor_proposto=Decimal("75000.00"),
            status=StausChoices.ENVIADA,
            **self.common_params
        )

    def test_aceite_concorrente_simultaneo(self):
        results = []
        barrier = threading.Barrier(2)

        def call_service():
            connection.close()
            barrier.wait()
            try:
                # Chama seu service com o nome do usuário
                res = ProposalService.aceitar_proposta(self.proposal.id, self.broker.username)
                results.append(("SUCCESS", res))
            except Exception as e:
                print(f"\nERRO NA THREAD: {str(e)}")
                results.append(("ERROR", str(e)))

        threads = [threading.Thread(target=call_service) for _ in range(2)]
        for t in threads: t.start()
        for t in threads: t.join()

        # Atualiza instâncias do banco
        self.proposal.refresh_from_db()
        self.precatorio.refresh_from_db()
        self.concorrente.refresh_from_db()

        # Asserts
        self.assertEqual(self.proposal.status, StausChoices.ACEITA)
        self.assertEqual(self.precatorio.status, StatusPrecatorioChoices.NEGOCIACAO)
        self.assertEqual(self.concorrente.status, StausChoices.REJEITADA)

        # Verifica se pelo menos um obteve sucesso (ou ambos se houver idempotência)
        successes = [r for r in results if r[0] == "SUCCESS"]
        self.assertGreaterEqual(len(successes), 1)