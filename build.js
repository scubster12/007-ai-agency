const fs = require('fs').promises;
const path = require('path');
const { minify } = require('terser');
const CleanCSS = require('clean-css');
const htmlMinifier = require('html-minifier');

const DIST_DIR = 'dist';
const SRC_FILES = {
    js: ['script.js', 'preferences.js'],
    css: ['styles.css'],
    html: ['index.html', 'preferences.html', 'privacy.html', 'terms.html']
};

async function ensureDistDir() {
    try {
        await fs.mkdir(DIST_DIR);
        await fs.mkdir(path.join(DIST_DIR, 'images'));
    } catch (err) {
        if (err.code !== 'EEXIST') throw err;
    }
}

async function minifyJS(file) {
    const content = await fs.readFile(file, 'utf8');
    const minified = await minify(content, {
        compress: {
            drop_console: true,
            dead_code: true
        },
        mangle: true
    });
    await fs.writeFile(path.join(DIST_DIR, file), minified.code);
    console.log(`✓ Minified ${file}`);
}

async function minifyCSS(file) {
    const content = await fs.readFile(file, 'utf8');
    const minified = new CleanCSS({
        level: 2,
        compatibility: '*'
    }).minify(content);
    await fs.writeFile(path.join(DIST_DIR, file), minified.styles);
    console.log(`✓ Minified ${file}`);
}

async function minifyHTML(file) {
    const content = await fs.readFile(file, 'utf8');
    const minified = htmlMinifier.minify(content, {
        collapseWhitespace: true,
        removeComments: true,
        minifyCSS: true,
        minifyJS: true
    });
    await fs.writeFile(path.join(DIST_DIR, file), minified);
    console.log(`✓ Minified ${file}`);
}

async function copyAssets() {
    const images = await fs.readdir('images');
    for (const image of images) {
        await fs.copyFile(
            path.join('images', image),
            path.join(DIST_DIR, 'images', image)
        );
    }
    console.log('✓ Copied assets');
}

async function build() {
    console.log('🔨 Building production bundle...');
    
    try {
        await ensureDistDir();

        // Minify all files in parallel
        await Promise.all([
            ...SRC_FILES.js.map(minifyJS),
            ...SRC_FILES.css.map(minifyCSS),
            ...SRC_FILES.html.map(minifyHTML)
        ]);

        await copyAssets();
        
        console.log('✨ Build complete! Files written to /dist');
    } catch (err) {
        console.error('❌ Build failed:', err);
        process.exit(1);
    }
}

build();
