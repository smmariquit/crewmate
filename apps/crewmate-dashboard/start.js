import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { join } from 'path';

const PORT = process.env.PORT || 3000;

// Check if dist folder exists
if (!existsSync(join(process.cwd(), 'dist'))) {
  console.log('Building the application...');
  try {
    execSync('npm run build', { stdio: 'inherit' });
    console.log('Build completed successfully!');
  } catch (error) {
    console.error('Build failed:', error.message);
    process.exit(1);
  }
}

console.log(`Starting server on port ${PORT}...`);
execSync(`npx serve -s dist -l ${PORT}`, { stdio: 'inherit' }); 