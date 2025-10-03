# ConfirmDialog Component

Sistema de diálogo de confirmação global e reutilizável para a plataforma ORBE.

## Características

- ✅ **Global**: Um único diálogo usado em toda a aplicação
- 🎨 **Flexível**: Múltiplas variantes visuais (default, warning, danger, success, info)
- 🔒 **Seguro**: Suporte para confirmação por input (ações críticas)
- ⚡ **Assíncrono**: Promise-based API
- 🌐 **Acessível**: Suporte completo a teclado e leitores de tela
- 📱 **Responsivo**: Adapta-se a diferentes tamanhos de tela

## Como Usar

### 1. Confirmação Simples

```typescript
import { useConfirm } from '@/composables/useConfirm'

const { confirm } = useConfirm()

const handleDelete = async () => {
  const confirmed = await confirm({
    title: 'Excluir Item',
    message: 'Tem certeza que deseja excluir este item?',
    icon: 'mdi-delete',
    variant: 'danger',
    confirmText: 'Excluir',
    cancelText: 'Cancelar'
  })

  if (confirmed) {
    // Executar ação
    await deleteItem()
  }
}
```

### 2. Confirmação com Input (Ações Críticas)

```typescript
const handleDeleteAccount = async () => {
  const confirmed = await confirm({
    title: 'Excluir Conta Permanentemente',
    message: 'Esta ação não pode ser desfeita. Digite "CONFIRMAR" para prosseguir.',
    icon: 'mdi-alert-octagon',
    variant: 'danger',
    confirmText: 'Excluir Conta',
    cancelText: 'Cancelar',
    requireInput: true,
    inputLabel: 'Confirmação',
    inputPlaceholder: 'Digite CONFIRMAR',
    inputValidation: 'CONFIRMAR'
  })

  if (confirmed) {
    await deleteAccount()
  }
}
```

### 3. Confirmação com Loading State

```typescript
import { useConfirm } from '@/composables/useConfirm'

const { confirm, setLoading, close } = useConfirm()

const handleApprove = async (item) => {
  const confirmed = await confirm({
    title: 'Aprovar Solicitação',
    message: `Deseja aprovar a solicitação de ${item.name}?`,
    icon: 'mdi-check-circle',
    variant: 'success',
    confirmText: 'Aprovar',
    persistent: true // Não fecha ao clicar fora
  })

  if (confirmed) {
    setLoading(true) // Mostra loading no botão

    try {
      await api.approve(item.id)
      close() // Fecha o diálogo manualmente
    } catch (error) {
      setLoading(false) // Remove loading, mantém diálogo aberto
      // Mostrar erro
    }
  }
}
```

### 4. Confirmação com Conteúdo Customizado

```vue
<template>
  <button @click="showCustomConfirm">Abrir</button>
</template>

<script setup>
import { useConfirm } from '@/composables/useConfirm'

const { confirm } = useConfirm()

const showCustomConfirm = async () => {
  // Para conteúdo customizado, use slots no componente diretamente
  // ou construa uma mensagem HTML
  const confirmed = await confirm({
    title: 'Múltiplas Ações',
    message: `
      <ul>
        <li>Item A será removido</li>
        <li>Item B será arquivado</li>
        <li>Item C será notificado</li>
      </ul>
    `,
    icon: 'mdi-information',
    variant: 'warning'
  })
}
</script>
```

## API Reference

### Props (ConfirmOptions)

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| `title` | `string` | - | **Obrigatório**. Título do diálogo |
| `message` | `string` | `''` | Mensagem de confirmação |
| `icon` | `string` | `undefined` | Ícone Material Design (ex: `mdi-delete`) |
| `variant` | `'default' \| 'warning' \| 'danger' \| 'success' \| 'info'` | `'default'` | Estilo visual |
| `confirmText` | `string` | `'Confirmar'` | Texto do botão de confirmação |
| `cancelText` | `string` | `'Cancelar'` | Texto do botão de cancelamento |
| `maxWidth` | `string \| number` | `500` | Largura máxima do diálogo |
| `persistent` | `boolean` | `false` | Se `true`, não fecha ao clicar fora |
| `requireInput` | `boolean` | `false` | Requer input de confirmação |
| `inputLabel` | `string` | `''` | Label do campo de input |
| `inputPlaceholder` | `string` | `''` | Placeholder do input |
| `inputValidation` | `string` | `''` | Texto que deve ser digitado para confirmar |

### Métodos (useConfirm)

| Método | Parâmetros | Retorno | Descrição |
|--------|------------|---------|-----------|
| `confirm()` | `options: ConfirmOptions` | `Promise<boolean>` | Abre o diálogo e retorna promise |
| `setLoading()` | `loading: boolean` | `void` | Define estado de loading |
| `close()` | - | `void` | Fecha o diálogo manualmente |

## Variantes Visuais

### Default (Azul)
```typescript
variant: 'default' // Azul ORBE (#304E69)
```

### Warning (Laranja)
```typescript
variant: 'warning' // Ações que requerem atenção
```

### Danger (Vermelho)
```typescript
variant: 'danger' // Ações destrutivas (deletar, remover)
```

### Success (Verde)
```typescript
variant: 'success' // Ações positivas (aprovar, confirmar)
```

### Info (Azul Claro)
```typescript
variant: 'info' // Informações importantes
```

## Exemplos de Uso Real (ORBE Platform)

### 1. Aprovar Doação (Finance)
```typescript
const approveDonation = async (donation: DonationRequest) => {
  const confirmed = await confirm({
    title: 'Aprovar Solicitação',
    message: `Deseja aprovar a solicitação para "${donation.recipient_name}" no valor de R$ ${donation.amount.toFixed(2)}?`,
    icon: 'mdi-check-circle',
    variant: 'success',
    confirmText: 'Aprovar',
    cancelText: 'Cancelar'
  })

  if (confirmed) {
    await api.approveDonation(donation.id)
  }
}
```

### 2. Excluir Caso de Assistência
```typescript
const deleteCase = async (assistanceCase: AssistanceCase) => {
  const confirmed = await confirm({
    title: 'Excluir Caso',
    message: `Tem certeza que deseja excluir o caso "${assistanceCase.title}"? Esta ação não pode ser desfeita.`,
    icon: 'mdi-delete-alert',
    variant: 'danger',
    confirmText: 'Excluir Permanentemente',
    cancelText: 'Cancelar',
    requireInput: true,
    inputValidation: 'EXCLUIR'
  })

  if (confirmed) {
    await api.deleteCase(assistanceCase.id)
  }
}
```

### 3. Cancelar Membro (Requer Confirmação Escrita)
```typescript
const cancelMembership = async (user: User) => {
  const confirmed = await confirm({
    title: 'Cancelar Associação',
    message: `ATENÇÃO: Cancelar a associação de ${user.name} removerá todos os dados e acessos. Digite o email do membro para confirmar.`,
    icon: 'mdi-account-remove',
    variant: 'danger',
    confirmText: 'Cancelar Associação',
    cancelText: 'Voltar',
    requireInput: true,
    inputLabel: 'Email do membro',
    inputValidation: user.email,
    persistent: true
  })

  if (confirmed) {
    await api.cancelMembership(user.id)
  }
}
```

## Boas Práticas

### ✅ DO

- Use `variant: 'danger'` para ações destrutivas
- Use `requireInput` para ações irreversíveis
- Forneça mensagens claras e contextuais
- Use ícones apropriados para reforçar a intenção
- Personalize textos dos botões para refletir a ação

### ❌ DON'T

- Não use para mensagens simples (use Snackbar)
- Não abuse de confirmações (só para ações críticas)
- Não use textos genéricos ("Tem certeza?")
- Não omita o ícone em confirmações importantes
- Não use `persistent: true` sem necessidade

## Acessibilidade

- ✅ Suporte completo a navegação por teclado
- ✅ Enter confirma, Escape cancela
- ✅ Foco automático no botão primário
- ✅ ARIA labels apropriados
- ✅ Contraste adequado (WCAG AA)

## Integração com i18n (Futuro)

```typescript
// TODO: Adicionar suporte a tradução
const confirmed = await confirm({
  title: t('confirmations.delete.title'),
  message: t('confirmations.delete.message', { name: item.name }),
  confirmText: t('common.delete'),
  cancelText: t('common.cancel')
})
```

---

**Desenvolvido para ORBE Platform**
Componente principal de confirmação seguindo Material Design 3 e padrões de UX.
