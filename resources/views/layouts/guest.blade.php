<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">

        <title>{{ config('app.name', 'Keluarga Somat') }}</title>

        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=figtree:400,500,600&display=swap" rel="stylesheet" />

        @vite(['resources/css/app.css', 'resources/js/app.js'])

        <style>
            .logo {
                width: 40vh;
                height: auto;
            }
        </style>
    </head>
    <body class="font-sans text-gray-900 antialiased">
        {{-- [DIUBAH] Latar belakang kini menggunakan gradien biru langit yang lembut --}}
        <div class="min-h-screen flex flex-col sm:justify-center items-center pt-6 sm:pt-0 bg-gradient-to-b from-sky-50 to-sky-200">

            {{-- [DIUBAH] Logo dan judul aplikasi ditempatkan di atas kartu --}}
            <div class="mb-6 text-center">
                <a href="/">
                    <img src="{{ asset('assets/img/Logo_Keluarga_Somat.jpeg') }}" alt="Logo" class="logo">
                </a>
                <h1 class="mt-2 text-2xl font-bold text-gray-700">{{ config('app.name', 'Keluarga Somat') }}</h1>
            </div>

            <div class="w-full sm:max-w-lg">
                {{ $slot }}
            </div>
        </div>
    </body>
</html>
