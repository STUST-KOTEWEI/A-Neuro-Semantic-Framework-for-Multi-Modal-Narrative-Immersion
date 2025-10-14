import 'dotenv/config';
import { listModels } from '@genkit-ai/googleai/list-models';

async function main() {
  const models = await listModels(
    'https://generativelanguage.googleapis.com',
    process.env.GOOGLE_API_KEY
  );
  console.log(models);
}

main();
