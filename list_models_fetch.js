import 'dotenv/config';
import fetch from 'node-fetch';

async function main() {
  const baseUrl = 'https://generativelanguage.googleapis.com';
  const apiKey = process.env.GOOGLE_API_KEY;
  const url = `${baseUrl}/v1beta/models?pageSize=1000&key=${apiKey}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log(JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('Error fetching models:', error);
  }
}

main();
