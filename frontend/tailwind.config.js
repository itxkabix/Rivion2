/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,jsx}",
    ],
    theme: {
        extend: {
            colors: {
                teal: {
                    50: '#f0fdfa',
                    500: '#14b8a6',
                    600: '#0d9488',
                },
            },
        },
    },
    plugins: [],
}
