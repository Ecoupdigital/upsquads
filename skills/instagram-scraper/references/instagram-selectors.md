# Instagram DOM Selectors & Patterns

> Atualizado em: 2026-03-20. Instagram muda frequentemente — atualize este arquivo quando seletores quebrarem.

## Perfil

### Links de posts no grid
```javascript
// Posts e reels no grid do perfil
document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]')
```

### Metadados do perfil
```javascript
// Bio, seguidores etc — extrair do snapshot/accessibility tree
// Alternativa via meta tags:
document.querySelector('meta[property="og:description"]')?.content
```

## Post Individual

### Legenda completa
```javascript
// A legenda geralmente está em um h1 ou span com dir="auto"
// Expandir "mais" primeiro se truncada
document.querySelector('span[dir="auto"]')  // primeiro resultado longo
```

### Data de publicação
```javascript
document.querySelector('time[datetime]')?.getAttribute('datetime')
```

### Elemento de vídeo
```javascript
document.querySelector('video')?.src
// Pode estar em blob: — nesse caso usar yt-dlp
```

### Carrossel — botão próximo
```
// No snapshot/accessibility tree, procurar por:
// - Botão com aria-label "Next" ou "Próximo"
// - Botão com SVG de seta para direita
// Referência no snapshot: button com texto "Next"
```

### Detecção de tipo de post
```javascript
// Vídeo: presença de <video> element
// Carrossel: presença de botão "Next" ou indicadores de slide (dots)
// Imagem: nenhum dos acima, apenas <img> no container do post
```

## Login Wall / Bloqueios

### Detecção via snapshot
- Texto "Log in" ou "Sign up" proeminente
- Texto "This account is private"
- Texto "Sorry, this page isn't available"
- Modal de login sobrepondo conteúdo

## Scroll

```javascript
// Scroll suave para carregar mais posts
window.scrollBy({ top: window.innerHeight * 2, behavior: 'smooth' })
```
