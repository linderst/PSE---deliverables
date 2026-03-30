/**
 * Converts a German-language string to a URL-friendly slug.
 * Transliterates German umlauts (oe, ae, ue, ss) and strips
 * non-alphanumeric characters. Returns "diagnose" for empty input.
 *
 * @param {string} text - The input text to slugify
 * @returns {string} URL-safe lowercase slug (e.g. "diabetes-mellitus-typ-2")
 * @example
 * slugify("Oesophagitis")   // => "oesophagitis"
 * slugify("Rueckenschmerz") // => "rueckenschmerz"
 * slugify("")               // => "diagnose"
 */
export const slugify = (text) => {
  if (!text) return "diagnose";
  return text.toLowerCase()
    .replace(/ö/g, 'oe').replace(/ä/g, 'ae').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)+/g, '');
};

/**
 * Converts plain text (typically from the Gemini API) to a sanitised HTML
 * object suitable for React's dangerouslySetInnerHTML.
 *
 * Applies basic markdown-like formatting:
 * - Double newlines become paragraph breaks ({@code <p>})
 * - Single newlines become {@code <br>}
 * - {@code **bold**} becomes {@code <strong>bold</strong>}
 *
 * @param {string} text - Raw text from the backend AI response
 * @returns {{ __html: string }} Object with an __html key for dangerouslySetInnerHTML
 */
export const formatText = (text) => {
  if (!text) return { __html: '' };
  // Very basic formatting: newlines to <br>, **text** to <strong>text</strong>
  const formatted = text
    .split(/\n\n+/)
    .map(p => `<p>${p.replace(/\n/g,'<br>').replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')}</p>`)
    .join('');
  return { __html: formatted };
};
