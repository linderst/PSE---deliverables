export const slugify = (text) => {
  if (!text) return "diagnose";
  return text.toLowerCase()
    .replace(/ö/g, 'oe').replace(/ä/g, 'ae').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)+/g, '');
};

export const formatText = (text) => {
  if (!text) return { __html: '' };
  // Very basic formatting: newlines to <br>, **text** to <strong>text</strong>
  const formatted = text
    .split(/\n\n+/)
    .map(p => `<p>${p.replace(/\n/g,'<br>').replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')}</p>`)
    .join('');
  return { __html: formatted };
};
