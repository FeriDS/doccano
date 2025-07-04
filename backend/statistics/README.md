# API de Estatísticas - Documentação de Exportação

## Endpoints de Exportação

### 1. Exportar Estatísticas em CSV
**GET** `/v1/projects/{project_id}/statistics/export/csv`

Exporta as estatísticas de anotação em formato CSV.

#### Parâmetros de Query (Opcionais)
- `start_date` (string): Data de início no formato YYYY-MM-DD
- `end_date` (string): Data de fim no formato YYYY-MM-DD  
- `label` (string): Filtro por categoria/label específico
- `resolved` (string): Filtro por status resolvido ("true" ou "false")
- `perspective` (string): Filtro por perspectiva
- `perspective_{field_id}` (string): Filtros específicos de campos de perspectiva

#### Exemplo de Uso
```bash
# Exportar todas as estatísticas
GET /v1/projects/123/statistics/export/csv

# Exportar com filtros de data
GET /v1/projects/123/statistics/export/csv?start_date=2025-01-01&end_date=2025-01-31

# Exportar com filtro de categoria
GET /v1/projects/123/statistics/export/csv?label=positive

# Exportar apenas desacordos não resolvidos
GET /v1/projects/123/statistics/export/csv?resolved=false
```

#### Resposta
- **Content-Type**: `text/csv`
- **Content-Disposition**: `attachment; filename=annotation_statistics.csv`
- **Body**: Arquivo CSV com as estatísticas

### 2. Exportar Estatísticas em PDF
**GET** `/v1/projects/{project_id}/statistics/export/pdf`

Exporta as estatísticas de anotação em formato PDF.

#### Parâmetros de Query (Opcionais)
- `start_date` (string): Data de início no formato YYYY-MM-DD
- `end_date` (string): Data de fim no formato YYYY-MM-DD
- `label` (string): Filtro por categoria/label específico
- `resolved` (string): Filtro por status resolvido ("true" ou "false")
- `perspective` (string): Filtro por perspectiva
- `perspective_{field_id}` (string): Filtros específicos de campos de perspectiva

#### Exemplo de Uso
```bash
# Exportar todas as estatísticas
GET /v1/projects/123/statistics/export/pdf

# Exportar com filtros de data
GET /v1/projects/123/statistics/export/pdf?start_date=2025-01-01&end_date=2025-01-31

# Exportar com filtro de categoria
GET /v1/projects/123/statistics/export/pdf?label=positive
```

#### Resposta
- **Content-Type**: `application/pdf`
- **Content-Disposition**: `attachment; filename=annotation_statistics.pdf`
- **Body**: Arquivo PDF com as estatísticas

## Conteúdo dos Relatórios

### CSV
O arquivo CSV contém as seguintes seções:
1. **Label Distribution**: Distribuição de labels com contagem e percentagem
2. **Perspective Distribution**: Distribuição por perspectiva (se aplicável)
3. **Disagreement by Category**: Desacordos por categoria
4. **Perspective Patterns**: Padrões de perspectiva com taxas de acordo/desacordo

### PDF
O arquivo PDF contém:
1. **Título**: "Annotation Statistics Report"
2. **Tabela de Desacordos**: Lista de desacordos encontrados com:
   - Text ID
   - Category
   - Type
   - Status

## Autenticação
Todos os endpoints requerem autenticação e permissões de administrador ou staff do projeto.

## Códigos de Erro
- `400 Bad Request`: Formato de exportação não especificado ou parâmetros inválidos
- `401 Unauthorized`: Usuário não autenticado
- `403 Forbidden`: Usuário sem permissões adequadas
- `500 Internal Server Error`: Erro interno durante a exportação

## Exemplo de Integração Frontend

```javascript
// Exportar CSV
const exportCSV = async (projectId, filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`/v1/projects/${projectId}/statistics/export/csv?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'annotation_statistics.csv';
    a.click();
  }
};

// Exportar PDF
const exportPDF = async (projectId, filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`/v1/projects/${projectId}/statistics/export/pdf?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'annotation_statistics.pdf';
    a.click();
  }
};
``` 