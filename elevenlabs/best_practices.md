# Best practices

> Learn how to control delivery, pronunciation, emotion, and optimize text for speech.

This guide provides techniques to enhance text-to-speech outputs using ElevenLabs models. Experiment with these methods to discover what works best for your needs.

---

## Controls

> **Info:** We are actively working on *Director's Mode* to give you even greater control over outputs.

These techniques provide a practical way to achieve nuanced results until advanced features like *Director's Mode* are rolled out.

### Pauses

> **Info:** Eleven v3 does not support SSML break tags. Use the techniques described in the [Prompting Eleven v3](https://www.google.com/search?q=%23prompting-eleven-v3) section for controlling pauses with v3.

Use `<break time="x.xs" />` for natural pauses up to 3 seconds.

> **Note:** Using too many break tags in a single generation can cause instability. The AI might speed up, or introduce additional noises or audio artifacts. We are working on resolving this.

```text
"Hold on, let me think." <break time="1.5s" /> "Alright, I've got it."

```

* **Consistency:** Use `<break>` tags consistently to maintain natural speech flow. Excessive use can lead to instability.
* **Voice-Specific Behavior:** Different voices may handle pauses differently, especially those trained with filler sounds like "uh" or "ah."

Alternatives to `<break>` include dashes (`-` or `--`) for short pauses or ellipses (`...`) for hesitant tones. However, these are less consistent.

```text
"It… well, it might work." "Wait — what's that noise?"

```

---

### Pronunciation

#### IPA with Eleven v3

The [Eleven v3](https://www.google.com/search?q=/docs/overview/models%23eleven-v3) model (`eleven_v3`) includes native support for International Phonetic Alphabet (IPA) transcription across 70+ languages, allowing precise control over word and phrase pronunciation without XML tags.

Unlike older models that require XML-style phoneme tags, v3 natively understands IPA symbols when wrapped in forward slashes directly in your text:

```text
"/IPA_transcription/"

```

The IPA transcription should be:

* Enclosed in forward slashes (`/`) at the beginning and end
* Written using standard IPA symbols
* Wrapped in double quotes when passed as a string parameter

**Code examples**

```python
# Python
from elevenlabs import ElevenLabs

client = ElevenLabs()
audio = client.text_to_speech.convert(
    voice_id="21m00Tcm4TlvDq8ikWAM",
    text='The term "/ˌbaɪoʊˈkemɪstri/" refers to the study of chemical processes.',
    model_id="eleven_v3",
)

```

```typescript
// TypeScript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient();

const audio = await client.textToSpeech.convert("21m00Tcm4TlvDq8ikWAM", {
  text: 'The city of "/ˌsænfrənˈsɪskoʊ/" is located in California.',
  modelId: "eleven_v3",
});

```

```bash
# cURL
curl -X POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id} \
  -H "xi-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The concept of \"/fəˈnɛtɪks/\" is central to linguistics.",
    "model_id": "eleven_v3"
  }'

```

You can include multiple IPA transcriptions in a single text string:

```python
# Python
from elevenlabs import ElevenLabs

client = ElevenLabs()
text = 'The medication "/ɡluːˈkoʊs/" and "/ˌɪnsjəˈlɪn/" are commonly used to manage conditions like "/ˌdaɪəˈbiːtiːz/".'
audio = client.text_to_speech.convert(
    voice_id="21m00Tcm4TlvDq8ikWAM",
    text=text,
    model_id="eleven_v3",
)

```

```typescript
// TypeScript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient();
const text =
  'The medication "/ɡluːˈkoʊs/" and "/ˌɪnsjəˈlɪn/" are commonly used to manage conditions like "/ˌdaɪəˈbiːtiːz/".';
const audio = await client.textToSpeech.convert("21m00Tcm4TlvDq8ikWAM", {
  text,
  modelId: "eleven_v3",
});

```

**Performance**

V3's IPA support achieves 80-90% pronunciation consistency. While significantly more reliable than v2's XML phoneme tags, it is not 100% consistent. The model may occasionally struggle with certain words or produce different outputs even with identical IPA transcriptions. We are continuing to improve IPA reliability.

**Best practices**

* Use standard IPA symbols from the [International Phonetic Alphabet chart](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet)
* Include stress markers: primary stress (`ˈ`) and secondary stress (`ˌ`) for multi-syllable words
* Apply selectively: only wrap specific words or phrases that need pronunciation control
* Test with your voice: different voices may interpret IPA slightly differently

**Troubleshooting**

* **Pronunciation is still incorrect:** Verify your IPA transcription is accurate using an IPA dictionary. Include stress markers (`ˈ` for primary stress, `ˌ` for secondary stress) for multi-syllable words. Test with different voices as some may interpret IPA more accurately than others.
* **Inconsistent results with the same IPA:** V3's IPA support is generally reliable but not perfect. The model may occasionally produce different outputs even with identical IPA transcriptions. If consistency is critical, test multiple generations and select the best result.

---

#### Phoneme tags for v2 models

Specify pronunciation using [SSML phoneme tags](https://en.wikipedia.org/wiki/Speech_Synthesis_Markup_Language) with v2 models. Supported alphabets include [CMU](https://en.wikipedia.org/wiki/CMU_Pronouncing_Dictionary) Arpabet and the [International Phonetic Alphabet (IPA)](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet).

> **Note:** Phoneme tags are only compatible with the `eleven_flash_v2` [model](https://www.google.com/search?q=/docs/overview/models).

```xml
<!-- CMU Arpabet Example -->
<phoneme alphabet="cmu-arpabet" ph="M AE1 D IH0 S AH0 N">
  Madison
</phoneme>

```

```xml
<!-- IPA Example -->
<phoneme alphabet="ipa" ph="ˈæktʃuəli">
  actually
</phoneme>

```

We recommend using CMU Arpabet for consistent and predictable results with v2 models. While IPA can be effective, CMU Arpabet generally offers more reliable performance.

Phoneme tags only work for individual words. If you have a name with a first and last name that you want to be pronounced a certain way, you will need to create a phoneme tag for each word.

Ensure correct stress marking for multi-syllable words to maintain accurate pronunciation:

```xml
<!-- Correct usage -->
<phoneme alphabet="cmu-arpabet" ph="P R AH0 N AH0 N S IY EY1 SH AH0 N">
  pronunciation
</phoneme>

```

```xml
<!-- Incorrect usage -->
<phoneme alphabet="cmu-arpabet" ph="P R AH N AH N S IY EY SH AH N">
  pronunciation
</phoneme>

```

---

#### Alias Tags

For models that don't support phoneme tags, you can try writing words more phonetically. You can also employ various tricks such as capital letters, dashes, apostrophes, or even single quotation marks around a single letter or letters.

As an example, a word like "trapezii" could be spelt "trapezIi" to put more emphasis on the "ii" of the word.

You can either replace the word directly in your text, or if you want to specify pronunciation using other words or phrases when using a pronunciation dictionary, you can use alias tags for this. This can be useful if you're generating using Multilingual v2, which doesn't support phoneme tags. You can use pronunciation dictionaries with ElevenCreative Studio, Dubbing Studio and Speech Synthesis via the API.

For example, if your text includes a name that has an unusual pronunciation that the AI might struggle with, you could use an alias tag to specify how you would like it to be pronounced:

```xml
<lexeme>
  <grapheme>Claughton</grapheme>
  <alias>Cloffton</alias>
</lexeme>

```

If you want to make sure that an acronym is always delivered in a certain way whenever it is encountered in your text, you can use an alias tag to specify this:

```xml
<lexeme>
  <grapheme>UN</grapheme>
  <alias>United Nations</alias>
</lexeme>

```

---

#### Pronunciation Dictionaries

Some of our tools, such as ElevenCreative Studio and Dubbing Studio, allow you to create and upload a pronunciation dictionary. These allow you to specify the pronunciation of certain words, such as character or brand names, or to specify how acronyms should be read.

Pronunciation dictionaries allow this functionality by enabling you to upload a lexicon or dictionary file that specifies pairs of words and how they should be pronounced, either using a phonetic alphabet or word substitutions.

Whenever one of these words is encountered in a project, the AI model will pronounce the word using the specified replacement.

To provide a pronunciation dictionary file, open the settings for a project and upload a file in either TXT or the [.PLS format](https://www.w3.org/TR/pronunciation-lexicon/). When a dictionary is added to a project it will automatically recalculate which pieces of the project will need to be re-converted using the new dictionary file and mark these as unconverted.

Currently we only support pronunciation dictionaries that specify replacements using phoneme or alias tags.

Both phonemes and aliases are sets of rules that specify a word or phrase they are looking for, referred to as a grapheme, and what it will be replaced with. Please note that searches are case sensitive. When checking for a replacement word in a pronunciation dictionary, the dictionary is checked from start to end and only the very first replacement is used.

**Pronunciation Dictionary examples**

Here are examples of pronunciation dictionaries in both CMU Arpabet and IPA, including a phoneme to specify the pronunciation of "Apple" and an alias to replace "UN" with "United Nations":

```xml
<!-- CMU Arpabet Example -->
<?xml version="1.0" encoding="UTF-8"?>
<lexicon version="1.0"
        xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon
          http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"
        alphabet="cmu-arpabet" xml:lang="en-GB">
  <lexeme>
    <grapheme>apple</grapheme>
    <phoneme>AE P AH L</phoneme>
  </lexeme>
  <lexeme>
    <grapheme>UN</grapheme>
    <alias>United Nations</alias>
  </lexeme>
</lexicon>

```

```xml
<!-- IPA Example -->
<?xml version="1.0" encoding="UTF-8"?>
<lexicon version="1.0"
        xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon
          http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"
        alphabet="ipa" xml:lang="en-GB">
  <lexeme>
    <grapheme>Apple</grapheme>
    <phoneme>ˈæpl̩</phoneme>
  </lexeme>
  <lexeme>
    <grapheme>UN</grapheme>
    <alias>United Nations</alias>
  </lexeme>
</lexicon>

```

To generate a pronunciation dictionary `.pls` file, there are a few open source tools available:

* [Sequitur G2P](https://github.com/sequitur-g2p/sequitur-g2p) - Open-source tool that learns pronunciation rules from data and can generate phonetic transcriptions.
* [Phonetisaurus](https://github.com/AdolfVonKleist/Phonetisaurus) - Open-source G2P system trained on existing dictionaries like CMUdict.
* [eSpeak](https://github.com/espeak-ng/espeak-ng) - Speech synthesizer that can generate phoneme transcriptions from text.
* [CMU Pronouncing Dictionary](https://github.com/cmusphinx/cmudict) - A pre-built English dictionary with phonetic transcriptions.

---

### Emotion

Convey emotions through narrative context or explicit dialogue tags. This approach helps the AI understand the tone and emotion to emulate.

```text
You're leaving?" she asked, her voice trembling with sadness. "That's it!" he exclaimed triumphantly.

```

Explicit dialogue tags yield more predictable results than relying solely on context, however the model will still speak out the emotional delivery guides. These can be removed in post-production using an audio editor if unwanted.

---

### Pace

The pacing of the audio is highly influenced by the audio used to create the voice. When creating your voice, we recommend using longer, continuous samples to avoid pacing issues like unnaturally fast speech.

For control over the speed of the generated audio, you can use the speed setting. This allows you to either speed up or slow down the speed of the generated speech. The speed setting is available in Text to Speech via the website and API, as well as in ElevenCreative Studio and Agents Platform. It can be found in the voice settings.

The default value is 1.0, which means that the speed is not adjusted. Values below 1.0 will slow the voice down, to a minimum of 0.7. Values above 1.0 will speed up the voice, to a maximum of 1.2. Extreme values may affect the quality of the generated speech.

Pacing can also be controlled by writing in a natural, narrative style.

```text
"I… I thought you'd understand," he said, his voice slowing with disappointment.

```

---

### Tips

**Common Issues**

* **Inconsistent pauses:** Ensure `<break time="x.xs" />` syntax is used for pauses.
* **Pronunciation errors:** Use CMU Arpabet or IPA phoneme tags for precise pronunciation.
* **Emotion mismatch:** Add narrative context or explicit tags to guide emotion. **Remember to remove any emotional guidance text in post-production.**

**Tips for Improving Output**
Experiment with alternative phrasing to achieve desired pacing or emotion. For complex sound effects, break prompts into smaller, sequential elements and combine results manually.

---

### Creative control

While we are actively developing a "Director's Mode" to give users even greater control over outputs, here are some interim techniques to maximize creativity and precision:

1. **Narrative styling:** Write prompts in a narrative style, similar to scriptwriting, to guide tone and pacing effectively.
2. **Layered outputs:** Generate sound effects or speech in segments and layer them together using audio editing software for more complex compositions.
3. **Phonetic experimentation:** If pronunciation isn't perfect, experiment with alternate spellings or phonetic approximations to achieve desired results.
4. **Manual adjustments:** Combine individual sound effects manually in post-production for sequences that require precise timing.
5. **Feedback iteration:** Iterate on results by tweaking descriptions, tags, or emotional cues.

---

## Text normalization

When using Text to Speech with complex items like phone numbers, zip codes and emails they might be mispronounced. This is often due to the specific items not being in the training set and smaller models failing to generalize how they should be pronounced. This guide will clarify when those discrepancies happen and how to have them pronounced correctly.

> **Tip:** Normalization is enabled by default for all TTS models to help improve pronunciation of numbers, dates, and other complex text elements.

### Why do models read out inputs differently?

Certain models are trained to read out numbers and phrases in a more human way. For instance, the phrase "$1,000,000" is correctly read out as "one million dollars" by the Eleven Multilingual v2 model. However, the same phrase is read out as "one thousand thousand dollars" by the Eleven Flash v2.5 model.

The reason for this is that the Multilingual v2 model is a larger model and can better generalize the reading out of numbers in a way that is more natural for human listeners, whereas the Flash v2.5 model is a much smaller model and so cannot.

#### Common examples

Text to Speech models can struggle with the following:

* Phone numbers ("123-456-7890")
* Currencies ("$47,345.67")
* Calendar events ("2024-01-01")
* Time ("9:23 AM")
* Addresses ("123 Main St, Anytown, USA")
* URLs ("[example.com/link/to/resource](https://www.google.com/search?q=https%3A%2F%2Fexample.com%2Flink%2Fto%2Fresource)")
* Abbreviations for units ("TB" instead of "Terabyte")
* Shortcuts ("Ctrl + Z")

---

### Mitigation

#### Use trained models

The simplest way to mitigate this is to use a TTS model that is trained to read out numbers and phrases in a more human way, such as the Eleven Multilingual v2 model. This however might not always be possible, for instance if you have a use case where low latency is critical (e.g. conversational agents).

#### Apply normalization in LLM prompts

In the case of using an LLM to generate the text for TTS, you can add normalization instructions to the prompt.

1. **Use clear and explicit prompts:** LLMs respond best to structured and explicit instructions. Your prompt should clearly specify that you want text converted into a readable format for speech.
2. **Handle different number formats:** Not all numbers are read out in the same way. Consider how different number types should be spoken:
* Cardinal numbers: 123 → "one hundred twenty-three"
* Ordinal numbers: 2nd → "second"
* Monetary values: $45.67 → "forty-five dollars and sixty-seven cents"
* Phone numbers: "123-456-7890" → "one two three, four five six, seven eight nine zero"
* Decimals & Fractions: "3.5" → "three point five", "⅔" → "two-thirds"
* Roman numerals: "XIV" → "fourteen" (or "the fourteenth" if a title)


3. **Remove or expand abbreviations:** Common abbreviations should be expanded for clarity:
* "Dr." → "Doctor"
* "Ave." → "Avenue"
* "St." → "Street" (but "St. Patrick" should remain)


You can request explicit expansion in your prompt:
> Expand all abbreviations to their full spoken forms.


4. **Alphanumeric normalization:** Not all normalization is about numbers, certain alphanumeric phrases should also be normalized for clarity:
* Shortcuts: "Ctrl + Z" → "control z"
* Abbreviations for units: "100km" → "one hundred kilometers"
* Symbols: "100%" → "one hundred percent"
* URLs: "elevenlabs.io/docs" → "eleven labs dot io slash docs"
* Calendar events: "2024-01-01" → "January first, two-thousand twenty-four"


5. **Consider edge cases:** Different contexts might require different conversions:
* Dates: "01/02/2023" → "January second, twenty twenty-three" or "the first of February, twenty twenty-three" (depending on locale)
* Time: "14:30" → "two thirty PM"


If you need a specific format, explicitly state it in the prompt.

##### Putting it all together

This prompt will act as a good starting point for most use cases:

```text
Convert the output text into a format suitable for text-to-speech. Ensure that numbers, symbols, and abbreviations are expanded for clarity when read aloud. Expand all abbreviations to their full spoken forms.

Example input and output:

"$42.50" → "forty-two dollars and fifty cents"
"£1,001.32" → "one thousand and one pounds and thirty-two pence"
"1234" → "one thousand two hundred thirty-four"
"3.14" → "three point one four"
"555-555-5555" → "five five five, five five five, five five five five"
"2nd" → "second"
"XIV" → "fourteen" - unless it's a title, then it's "the fourteenth"
"3.5" → "three point five"
"⅔" → "two-thirds"
"Dr." → "Doctor"
"Ave." → "Avenue"
"St." → "Street" (but saints like "St. Patrick" should remain)
"Ctrl + Z" → "control z"
"100km" → "one hundred kilometers"
"100%" → "one hundred percent"
"elevenlabs.io/docs" → "eleven labs dot io slash docs"
"2024-01-01" → "January first, two-thousand twenty-four"
"123 Main St, Anytown, USA" → "one two three Main Street, Anytown, United States of America"
"14:30" → "two thirty PM"
"01/02/2023" → "January second, two-thousand twenty-three" or "the first of February, two-thousand twenty-three", depending on locale of the user

```

---

#### Use Regular Expressions for preprocessing

If using code to prompt an LLM, you can use regular expressions to normalize the text before providing it to the model. This is a more advanced technique and requires some knowledge of regular expressions. Here are some simple examples:

```python
# normalize_text.py
# Be sure to install the inflect library before running this code
import inflect
import re

# Initialize inflect engine for number-to-word conversion
p = inflect.engine()

def normalize_text(text: str) -> str:
    # Convert monetary values
    def money_replacer(match):
        currency_map = {"$": "dollars", "£": "pounds", "€": "euros", "¥": "yen"}
        currency_symbol, num = match.groups()

        # Remove commas before parsing
        num_without_commas = num.replace(',', '')

        # Check for decimal points to handle cents
        if '.' in num_without_commas:
            dollars, cents = num_without_commas.split('.')
            dollars_in_words = p.number_to_words(int(dollars))
            cents_in_words = p.number_to_words(int(cents))
            return f"{dollars_in_words} {currency_map.get(currency_symbol, 'currency')} and {cents_in_words} cents"
        else:
            # Handle whole numbers
            num_in_words = p.number_to_words(int(num_without_commas))
            return f"{num_in_words} {currency_map.get(currency_symbol, 'currency')}"

    # Regex to handle commas and decimals
    text = re.sub(r"([$£€¥])(\d+(?:,\d{3})*(?:\.\d{2})?)", money_replacer, text)

    # Convert phone numbers
    def phone_replacer(match):
        return ", ".join(" ".join(p.number_to_words(int(digit)) for digit in group) for group in match.groups())

    text = re.sub(r"(\d{3})-(\d{3})-(\d{4})", phone_replacer, text)

    return text

# Example usage
print(normalize_text("$1,000"))      # "one thousand dollars"
print(normalize_text("£1000"))       # "one thousand pounds"
print(normalize_text("€1000"))       # "one thousand euros"
print(normalize_text("¥1000"))       # "one thousand yen"
print(normalize_text("$1,234.56"))   # "one thousand two hundred thirty-four dollars and fifty-six cents"
print(normalize_text("555-555-5555")) # "five five five, five five five, five five five five"

```

```typescript
// normalizeText.ts
// Be sure to install the number-to-words library before running this code
import { toWords } from "number-to-words";

function normalizeText(text: string): string {
  return (
    text
      // Convert monetary values (e.g., "$1000" → "one thousand dollars", "£1000" → "one thousand pounds")
      .replace(/([$£€¥])(\d+(?:,\d{3})*(?:\.\d{2})?)/g, (_, currency, num) => {
        // Remove commas before parsing
        const numWithoutCommas = num.replace(/,/g, "");

        const currencyMap: { [key: string]: string } = {
          $: "dollars",
          "£": "pounds",
          "€": "euros",
          "¥": "yen",
        };

        // Check for decimal points to handle cents
        if (numWithoutCommas.includes(".")) {
          const [dollars, cents] = numWithoutCommas.split(".");
          return `${toWords(Number.parseInt(dollars))} ${currencyMap[currency] || "currency"}${cents ? ` and ${toWords(Number.parseInt(cents))} cents` : ""}`;
        }

        // Handle whole numbers
        return `${toWords(Number.parseInt(numWithoutCommas))} ${currencyMap[currency] || "currency"}`;
      })

      // Convert phone numbers (e.g., "555-555-5555" → "five five five, five five five, five five five five")
      .replace(/(\d{3})-(\d{3})-(\d{4})/g, (_, p1, p2, p3) => {
        return `${spellOutDigits(p1)}, ${spellOutDigits(p2)}, ${spellOutDigits(p3)}`;
      })
  );
}

// Helper function to spell out individual digits as words (for phone numbers)
function spellOutDigits(num: string): string {
  return num
    .split("")
    .map((digit) => toWords(Number.parseInt(digit)))
    .join(" ");
}

// Example usage
console.log(normalizeText("$1,000")); // "one thousand dollars"
console.log(normalizeText("£1000")); // "one thousand pounds"
console.log(normalizeText("€1000")); // "one thousand euros"
console.log(normalizeText("¥1000")); // "one thousand yen"
console.log(normalizeText("$1,234.56")); // "one thousand two hundred thirty-four dollars and fifty-six cents"
console.log(normalizeText("555-555-5555")); // "five five five, five five five, five five five five"

```

---

## Prompting Eleven v3

This guide provides the most effective tags and techniques for prompting Eleven v3, including voice selection, changes in capitalization, punctuation, audio tags and multi-speaker dialogue. Experiment with these methods to discover what works best for your specific voice and use case.

> **Info:** Eleven v3 does not support SSML break tags. Use audio tags, punctuation (ellipses), and text structure to control pauses and pacing with v3.

### Voice selection

The most important parameter for Eleven v3 is the voice you choose. It needs to be similar enough to the desired delivery. For example, if the voice is shouting and you use the audio tag `[whispering]`, it likely won't work well.

When creating IVCs, you should include a broader emotional range than before. As a result, voices in the voice library may produce more variable results compared to the v2 and v2.5 models. We've compiled a [curated collection of voices for V3](https://elevenlabs.io/app/voice-library/collections/aF6JALq9R6tXwCczjhKH).

Choose voices strategically based on your intended use:

* **Emotionally diverse:** For expressive IVC voices, vary emotional tones across the recording—include both neutral and dynamic samples.
* **Targeted niche:** For specific use cases like sports commentary, maintain consistent emotion throughout the dataset.
* **Neutral:** Neutral voices tend to be more stable across languages and styles, providing reliable baseline performance.

> **Info:** Professional Voice Clones (PVCs) are currently not fully optimized for Eleven v3, resulting in potentially lower clone quality compared to earlier models. During this research preview stage it would be best to find an Instant Voice Clone (IVC) or designed voice for your project if you need to use v3 features.

---

### Settings

#### Stability

The stability slider is the most important setting in v3, controlling how closely the generated voice adheres to the original reference audio.

* **Creative:** More emotional and expressive, but prone to hallucinations.
* **Natural:** Closest to the original voice recording—balanced and neutral.
* **Robust:** Highly stable, but less responsive to directional prompts but consistent, similar to v2.

> **Note:** For maximum expressiveness with audio tags, use Creative or Natural settings. Robust reduces responsiveness to directional prompts.

---

### Audio tags

Eleven v3 introduces emotional control through audio tags. You can direct voices to laugh, whisper, act sarcastic, or express curiosity among many other styles. Speed is also controlled through audio tags.

> **Note:** The voice you choose and its training samples will affect tag effectiveness. Some tags work well with certain voices while others may not. Don't expect a whispering voice to suddenly shout with a `[shout]` tag.

#### Voice-related

These tags control vocal delivery and emotional expression:

* `[laughs]`, `[laughs harder]`, `[starts laughing]`, `[wheezing]`
* `[whispers]`
* `[sighs]`, `[exhales]`
* `[sarcastic]`, `[curious]`, `[excited]`, `[crying]`, `[snorts]`, `[mischievously]`

```text
[whispers] I never knew it could be this way, but I'm glad we're here.

```

#### Sound effects

Add environmental sounds and effects:

* `[gunshot]`, `[applause]`, `[clapping]`, `[explosion]`
* `[swallows]`, `[gulps]`

```text
[applause] Thank you all for coming tonight! [gunshot] What was that?

```

#### Unique and special

Experimental tags for creative applications:

* `[strong X accent]` (replace X with desired accent)
* `[sings]`, `[woo]`, `[fart]`

```text
[strong French accent] "Zat's life, my friend — you can't control everysing."

```

> **Warning:** Some experimental tags may be less consistent across different voices. Test thoroughly before production use.

---

### Punctuation

Punctuation significantly affects delivery in v3:

* **Ellipses (...)** add pauses and weight
* **Capitalization** increases emphasis
* **Standard punctuation** provides natural speech rhythm

```text
"It was a VERY long day [sigh] … nobody listens anymore."

```

---

### Single speaker examples

Use tags intentionally and match them to the voice's character. A meditative voice shouldn't shout; a hyped voice won't whisper convincingly.

#### Expressive monologue

```text
"Okay, you are NOT going to believe this.

You know how I've been totally stuck on that short story?

Like, staring at the screen for HOURS, just... nothing?

[frustrated sigh] I was seriously about to just trash the whole thing. Start over.

Give up, probably. But then!

Last night, I was just doodling, not even thinking about it, right?

And this one little phrase popped into my head. Just... completely out of the blue.

And it wasn't even for the story, initially.

But then I typed it out, just to see. And it was like... the FLOODGATES opened!

Suddenly, I knew exactly where the character needed to go, what the ending had to be...

It all just CLICKED. [happy gasp] I stayed up till, like, 3 AM, just typing like a maniac.

Didn't even stop for coffee! [laughs] And it's... it's GOOD! Like, really good.

It feels so... complete now, you know? Like it finally has a soul.

I am so incredibly PUMPED to finish editing it now.

It went from feeling like a chore to feeling like... MAGIC. Seriously, I'm still buzzing!"

```

#### Dynamic and humorous

```text
[laughs] Alright...guys - guys. Seriously.

[exhales] Can you believe just how - realistic - this sounds now?

[laughing hysterically] I mean OH MY GOD...it's so good.

Like you could never do this with the old model.

For example [pauses] could you switch my accent in the old model?

[dismissive] didn't think so. [excited] but you can now!

Check this out... [cute] I'm going to speak with a french accent now..and between you and me

[whispers] I don't know how. [happy] ok.. here goes. [strong French accent] "Zat's life, my friend — you can't control everysing."

[giggles] isn't that insane? Watch, now I'll do a Russian accent -

[strong Russian accent] "Dee Goldeneye eez fully operational and rready for launch."

[sighs] Absolutely, insane! Isn't it..? [sarcastic] I also have some party tricks up my sleeve..

I mean i DID go to music school.

[singing quickly] "Happy birthday to you, happy birthday to you, happy BIRTHDAY dear ElevenLabs... Happy birthday to youuu."

```