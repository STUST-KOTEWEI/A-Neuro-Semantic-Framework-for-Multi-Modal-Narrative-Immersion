import 'dotenv/config';
import { enableFirebaseTelemetry } from '@genkit-ai/firebase';
// import the Genkit and Google AI plugin libraries
import { gemini, googleAI } from '@genkit-ai/googleai';
import { genkit } from 'genkit';

enableFirebaseTelemetry();

// configure a Genkit instance
const ai = genkit({
  plugins: [googleAI()],
  model: gemini('gemini-pro'), // set default model
});

const helloFlow = ai.defineFlow('helloFlow', async (name) => {
  // make a generation request
  const { text } = await ai.generate(`Hello Gemini, my name is ${name}`);
  console.log(text);
});

helloFlow('Chris');
