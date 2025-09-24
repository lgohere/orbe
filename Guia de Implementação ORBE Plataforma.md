# DETALHES

📑 Sprint 01 — Plataforma ORBE (MVP)

🎯 Objetivo do Sprint

Construir o MVP funcional da plataforma ORBE, garantindo:
	•	Onboarding simplificado e acessível para membros (Google login + cadastro leve).
	•	Gestão de mensalidades via PIX (sem comprovante, apenas lembrete configurável).
	•	Gestão de doações via PIX (sem comprovante obrigatório).
	•	Registro de atendimentos (com comprovantes obrigatórios).
	•	Feed de comunicados (estilo cards, responsivo, mobile first).
	•	Governança de acesso mínima (SuperAdmin, Diretoria, Conselho Fiscal, Membro).
	•	Multilinguagem (PT-BR, EN, ES).
	•	Temas White/Black com design tokens definidos.
	•	UI/UX responsiva, acessível, moderna e intuitiva (mobile first, desktop-ready).

⸻

👥 Papéis e Governança de Acesso
	•	SuperAdmin: controla toda a plataforma.
	•	Diretoria: cria comunicados, lança atendimentos, visualiza mensalidades/doações.
	•	Conselho Fiscal: aprova atendimentos.
	•	Membro: recebe lembretes de mensalidade, acessa feed, visualiza transparência.

⸻

🗂 Backlog do Sprint

🔹 1. Autenticação & Cadastro
	•	Login social (Google) via django-allauth / dj-rest-auth.
	•	Cadastro leve (fallback) com wizard em Vue3:
	1.	Nome + Telefone (com DDI).
	2.	Email + Endereço.
	3.	Escolha do dia preferencial da mensalidade.
	4.	Termos de uso + política de privacidade.
	•	Envio automático de senha provisória por email (via Kestra).
	•	Primeiro login → força redefinição de senha.
	•	Esqueceu senha → reset via link de e-mail.

Critérios de aceitação
✅ Login com Google funcionando.
✅ Wizard dividido em 3–4 passos, estilo conversacional.
✅ Senha provisória enviada corretamente.
✅ Reset de senha operacional.

⸻

🔹 2. Mensalidade (R$ 60,00 fixos)
	•	Cada usuário define dia preferencial de vencimento (1–28).
	•	Sistema dispara e-mails automáticos (via Kestra + Celery Beat):
	•	D-0: lembrete amigável.
	•	D+3: lembrete de atraso.
	•	Registro interno de lembretes enviados.
	•	Transparência: relatório agregado por mês (ex.: “Arrecadado R$ X em mensalidades”).

Critérios de aceitação
✅ Membro recebe lembrete no dia correto.
✅ Configuração de vencimento salva por usuário.
✅ Relatório agregado mensal disponível para diretoria.

⸻

🔹 3. Doações
	•	Página com chave PIX + QR Code.
	•	Botão “Doe agora”.
	•	Registro interno de doação (valor informado opcional).
	•	Transparência: agregado mensal publicado em comunicados.

Critérios de aceitação
✅ Página de doações clara e simples.
✅ Registro opcional de valor.
✅ Relatório agregado publicado no feed.

⸻

🔹 4. Atendimentos (comprovantes obrigatórios)
	•	Diretoria cria atendimento (título, descrição pública, descrição interna, valor total).
	•	Upload de comprovantes/fotos obrigatórios.
	•	Conselho Fiscal revisa e aprova/reprova.
	•	Após aprovação → publicado no Mural de Transparência (feed).

Critérios de aceitação
✅ Diretoria consegue registrar atendimento.
✅ Upload de múltiplas imagens (com compressão/lazy load).
✅ Conselho Fiscal aprova via painel simples.
✅ Atendimentos aprovados aparecem no feed.

⸻

🔹 5. Feed de Comunicados
	•	Estilo rede social (cards verticais, scroll infinito).
	•	Tipos de posts:
	•	Comunicados da diretoria.
	•	Relatórios de mensalidades/doações.
	•	Atendimentos aprovados.
	•	Estrutura: título, resumo, imagem opcional, CTA “Ver mais”.

Critérios de aceitação
✅ Feed responsivo em mobile e desktop.
✅ Cards legíveis (tipografia 18px+, botões grandes).
✅ Posts categorizados (comunicado, financeiro, atendimento).

⸻

🔹 6. Multilinguagem (i18n)
	•	Backend: Django i18n ativado.
	•	Frontend: Vue-i18n com fallback pt-br.
	•	Idiomas disponíveis: PT-BR (default), EN, ES.
	•	Seletor no header (ícone 🌐 + idioma atual).

Critérios de aceitação
✅ Todas labels traduzíveis.
✅ Idioma detectado via navegador.
✅ Usuário pode mudar idioma manualmente.

⸻

🔹 7. Temas (white/black)
	•	White (default):
	•	Bg gradiente: #DDEAF4 → #FFFFFF
	•	Texto: #304E69, #000000
	•	Botões: #C79657
	•	Black:
	•	Bg gradiente: #304E69 → #5B7185
	•	Texto: #FFFFFF, #000000
	•	Botões: #C79657
	•	Toggle de tema fixo no header.
	•	Preferência salva em localStorage e UserProfile.

Critérios de aceitação
✅ Tema troca em tempo real.
✅ Preferência persiste em login/logout.
✅ Contraste testado (mínimo WCAG AA).

⸻

🔹 8. Responsividade (UI/UX)
	•	Mobile first:
	•	Barra inferior fixa (Home, Mensalidade, Atendimentos, Conta).
	•	Cards full width.
	•	Desktop:
	•	Sidebar lateral fixa (Diretoria/CF).
	•	Painéis administrativos em grid/tabela.

Critérios de aceitação
✅ UI fluida em 360px (celular pequeno), 768px (tablet) e 1440px (desktop).
✅ Botões ≥ 48px de altura.
✅ Navegação clara para idosos (ícone + texto sempre).

⸻

🔹 9. Ícones (moderno + minimalista)
	•	Lib: unplugin-icons + Lucide/Phosphor.
	•	Wrapper <UiIcon> para troca automática (tema claro = Lucide, escuro/alto contraste = Phosphor Fill).

Critérios de aceitação
✅ Todos ícones consistentes.
✅ Acessibilidade: aria-label ou aria-hidden.
✅ Nenhum SVG externo dinâmico (segurança).

⸻

🏗 Arquitetura Técnica

Backend (Django + DRF)
	•	Apps: users, finance, assistance, feed.
	•	DB: PostgreSQL.
	•	Cache/Sessão: Redis.
	•	Armazenamento de arquivos: Hetzner Object Storage (S3).
	•	i18n: gettext_lazy.
	•	Auth: Django + Google OAuth.

Frontend (Vue3 + TailwindCSS)
	•	Estrutura em layouts: MobileLayout, DesktopLayout.
	•	vue-i18n + unplugin-icons.
	•	Design tokens para cores, fontes, espaçamentos.
	•	Responsividade via Tailwind breakpoints.

Infra
	•	Deploy: Hetzner VPS 4GB/3vCPU, Docker.
	•	Proxy: Nginx.
	•	CDN/DNS: Cloudflare.
	•	Jobs: Celery + Kestra (e-mails e lembretes).
	•	Observabilidade: logs + métricas básicas (healthchecks).

⸻

📅 Cronograma (2 semanas)

Dia 1–2: Setup de projeto (Django + Vue + CI/CD no Hetzner).
Dia 3–5: Autenticação + Onboarding wizard.
Dia 6–7: Módulo Mensalidade (agendamento de lembrete via Kestra).
Dia 8–9: Doações + Atendimentos (comprovantes obrigatórios).
Dia 10: Feed de comunicados (cards responsivos).
Dia 11: i18n + troca de temas.
Dia 12: Ajustes de responsividade + ícones.
Dia 13: Testes (mobile + desktop + usabilidade idoso).
Dia 14: Deploy + revisão em produção.

⸻

✅ Critérios de Conclusão do Sprint
	•	Cadastro leve funcional (Google + manual).
	•	Lembretes de mensalidade por email funcionando.
	•	Atendimentos com comprovantes anexados e aprovados pelo CF.
	•	Feed responsivo em mobile e desktop.
	•	Tradução PT/EN/ES ativa.
	•	Tema white/black trocável.
	•	Deploy rodando no Hetzner com logs e monitoramento básico.


# OUTROS DETALHES


🗂 Sprint 01 — Plano de Tarefas (Task Master)

🔹 Setup Inicial
	1.	Criar repositório Git (monorepo ou dois repos: backend / frontend).
	2.	Configurar CI/CD básico no Coolify (build + deploy dockerizado).
	3.	Backend Django:
	•	Inicializar projeto (django-admin startproject).
	•	Configurar apps: users, finance, assistance, feed.
	•	Banco local: SQLite (desenvolvimento).
	4.	Frontend Vue3:
	•	Criar projeto (npm init vue@latest).
	•	Instalar dependências: TailwindCSS, vue-i18n, unplugin-icons.
	•	Configurar rotas e layouts (MobileLayout, DesktopLayout).

⸻

�� Autenticação & Onboarding
	5.	Backend
	•	Configurar Django Allauth + dj-rest-auth (Google OAuth + login senha).
	•	Model UserProfile com campos: telefone, endereço, dia_vencimento.
	6.	Frontend
	•	Implementar wizard onboarding em 3–4 passos (conversacional).
	•	Conectar com API de criação de conta.
	•	Enviar senha provisória por e-mail (fluxo Kestra).
	•	Forçar redefinição de senha no primeiro login.

⸻

🔹 Mensalidade
	7.	Backend
	•	Model MembershipFee (user_id, competencymonth, amount=60, due_date).
	•	API para registrar vencimento preferencial.
	•	Endpoint de relatório agregado mensal.
	8.	Automação
	•	Kestra flow para enviar lembrete no dia do vencimento.
	•	Template de e-mail (D-0 e D+3).
	9.	Frontend
	•	Tela “Mensalidade”: mostra valor fixo + próximo vencimento.
	•	Permitir configurar/editar dia preferencial.

⸻

🔹 Doações
	10.	Backend
	•	Model Donation (opcional user_id, valor opcional, data).
	•	Endpoint de registro (para doações declaradas).
	11.	Frontend
	•	Página “Doe agora” → exibe chave PIX + QR.
	•	Formulário opcional para informar valor doado.
	•	Tela de transparência agregada mensal.

⸻

🔹 Atendimentos
	12.	Backend
	•	Model AssistanceCase (título, descrição_publica, descricao_interna, valor_total, status).
	•	Model Attachment vinculado (fotos/comprovantes).
	•	Workflow de aprovação: Diretoria cria → Conselho Fiscal aprova.
	13.	Frontend
	•	Formulário para Diretoria criar atendimento + upload obrigatório.
	•	Painel Conselho Fiscal: aprovar/reprovar.
	•	Publicação automática no feed quando aprovado.

⸻

🔹 Feed de Comunicados
	14.	Backend
	•	Model Post (tipo: comunicado, mensalidade, doação, atendimento).
	•	API para listar posts ordenados por data.
	15.	Frontend
	•	Componente <Feed> com cards estilo redes sociais.
	•	Scroll infinito/paginação.
	•	Suporte a posts de texto, imagens, relatórios.

⸻

🔹 Multilinguagem
	16.	Backend
	•	Ativar django-i18n e marcar strings com gettext_lazy.
	17.	Frontend
	•	Configurar vue-i18n com pt-br, en, es.
	•	Criar JSONs de tradução.
	•	Botão seletor de idioma no header (🌐).

⸻

🔹 Temas
	18.	Frontend
	•	Definir tokens de design (cores, fontes, espaçamentos).
	•	Implementar temas White/Black (CSS vars).
	•	Toggle no header.
	•	Persistência em localStorage + UserProfile.

⸻

🔹 Responsividade
	19.	Frontend
	•	Layout mobile-first (barra inferior fixa).
	•	Layout desktop (sidebar para diretoria/CF).
	•	Testes em breakpoints: 360px, 768px, 1440px.
	•	Garantir botões ≥ 48px e tipografia 18px+.

⸻

🔹 Ícones
	20.	Frontend
	•	Instalar unplugin-icons com coleções Lucide e Phosphor.
	•	Criar componente <UiIcon> comutando coleção por tema/contraste.
	•	Substituir todos ícones hardcoded por <UiIcon>.

⸻

🔹 Testes Locais
	21.	Rodar todo o sistema localmente com SQLite (Django) + npm run dev (Vue).
	22.	Verificar fluxos completos: cadastro, login, mensalidade, doação, atendimento.

⸻

🔹 Dockerização (para Coolify)
	23.	Criar Dockerfile para backend (Django + Gunicorn).
	24.	Criar Dockerfile para frontend (Vue3 + build estático).
	25.	Criar docker-compose.yml com serviços:
	•	backend (Django + Gunicorn)
	•	frontend (Vue3 build)
	•	redis
	•	postgres
	26.	Deploy via Coolify (Traefik já cuida do proxy).

⸻

📅 Cronograma (Task Master - 2 semanas)
	•	Dia 1–2 → Setup repositórios + CI/CD Coolify + projetos (Django, Vue).
	•	Dia 3–4 → Autenticação + Onboarding wizard.
	•	Dia 5 → Model & API Mensalidade + integração Kestra (lembretes).
	•	Dia 6 → Página de Mensalidade no frontend.
	•	Dia 7 → Doações (API + frontend).
	•	Dia 8–9 → Atendimentos (API + frontend + fluxo aprovação CF).
	•	Dia 10 → Feed de comunicados (API + frontend).
	•	Dia 11 → Multilinguagem (pt/en/es).
	•	Dia 12 → Temas White/Black.
	•	Dia 13 → Responsividade (mobile-first + desktop).
	•	Dia 14 → Ícones + testes locais + dockerização + deploy no Coolify.