<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="apple-touch-icon" sizes="76x76" href="{{ asset('assets/img/apple-icon.png') }}" />
    <link rel="icon" type="image/png" href="{{ asset('assets/img/favicon.png') }}" />
    <title>@yield('title', 'Dashboard')</title>

    <!-- Fonts and icons -->
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700" rel="stylesheet" />
    <script src="https://kit.fontawesome.com/42d5adcbca.js" crossorigin="anonymous"></script>
    <link href="{{ asset('assets/css/nucleo-icons.css') }}" rel="stylesheet" />
    <link href="{{ asset('assets/css/nucleo-svg.css') }}" rel="stylesheet" />
    <script src="https://unpkg.com/@popperjs/core@2"></script>
    <link href="{{ asset('assets/css/soft-ui-dashboard-tailwind.css?v=1.0.5') }}" rel="stylesheet" />

    <!-- Tailwind & Vite -->
    <script src="https://cdn.tailwindcss.com"></script>
    @vite('resources/css/app.css')
</head>

<body class="m-0 font-sans text-base antialiased font-normal leading-default bg-gray-50 text-slate-500">

    <!-- Sidenav -->
    <aside class="max-w-62.5 ease-nav-brand z-990 fixed inset-y-0 my-4 ml-4 block w-full -translate-x-full flex-wrap items-center justify-between overflow-y-auto rounded-2xl border-0 bg-white p-0 antialiased shadow-[10px_0_15px_-5px_rgba(0,0,0,0.05)] transition-transform duration-200 xl:left-0 xl:translate-x-0">
        <div class="h-19.5">
            <i class="absolute top-0 right-0 hidden p-4 opacity-50 cursor-pointer fas fa-times text-slate-400 xl:hidden" sidenav-close></i>
            <a class="block px-8 py-6 m-0 text-sm whitespace-nowrap text-slate-700" href="javascript:;" target="_blank">
                <img src="{{ asset('assets/img/Logo_Keluarga_Somat.jpeg') }}" class="inline h-full max-w-full transition-all duration-200 ease-nav-brand max-h-8" alt="main_logo" />
                <span class="ml-1 font-semibold transition-all duration-200 ease-nav-brand">Word Cloud</span>
            </a>
        </div>

        <hr class="h-px mt-0 bg-transparent bg-gradient-to-r from-transparent via-black/40 to-transparent" />
        <div class="items-center block w-auto max-h-screen overflow-auto h-sidenav grow basis-full">
            <ul class="flex flex-col pl-0 mb-0">
                <li class="mt-0.5 w-full">
                    <a class="py-2.7 text-sm ease-nav-brand my-0 mx-4 flex items-center whitespace-nowrap rounded-lg px-4 transition-colors
                        {{ request()->routeIs('wordcloud.index') ? 'bg-white font-semibold shadow-soft-xl text-slate-700' : 'text-slate-500' }}"
                        href="{{ route('wordcloud.index') }}">

                        {{-- [DIUBAH] Ikon hanya akan muncul jika menu ini aktif --}}
                        @if(request()->routeIs('wordcloud.index'))
                            <div class="mr-2 flex h-8 w-8 items-center justify-center rounded-full bg-white text-center xl:p-1.5">
                                <img src="{{ asset('assets/img/Logo_Keluarga_Somat.jpeg') }}" alt="Somat Logo" class="h-6 w-6 rounded-full object-cover">
                            </div>
                        @endif

                        <span class="ml-1 duration-300 opacity-100 pointer-events-none ease-soft">Dashboard</span>
                    </a>
                </li>

                <li class="mt-0.5 w-full">
                    <a class="py-2.7 text-sm ease-nav-brand my-0 mx-4 flex items-center whitespace-nowrap rounded-lg px-4 transition-colors
                        {{ request()->routeIs('wordcloud.config') ? 'bg-white font-semibold shadow-soft-xl text-slate-700' : 'text-slate-500' }}"
                        href="{{ route('wordcloud.config') }}">

                        {{-- [DIUBAH] Ikon hanya akan muncul jika menu ini aktif --}}
                        @if(request()->routeIs('wordcloud.config'))
                            <div class="mr-2 flex h-8 w-8 items-center justify-center rounded-full bg-white text-center xl:p-1.5">
                                <img src="{{ asset('assets/img/Logo_Keluarga_Somat.jpeg') }}" alt="Somat Logo" class="h-6 w-6 rounded-full object-cover">
                            </div>
                        @endif

                        <span class="ml-1 duration-300 opacity-100 pointer-events-none ease-soft">Konfigurasi</span>
                    </a>
                </li>

                <li class="nav-item">
                    <a href="{{ route('logout') }}"
                    onclick="event.preventDefault(); document.getElementById('logout-form').submit();"
                    class="flex items-center p-4 text-sm font-semibold text-gray-700 hover:bg-gray-100 rounded-lg">
                        <img src="https://cdn-icons-png.flaticon.com/512/18273/18273095.png" class="mr-2" style="width: 25px; height: auto;" alt="Logout">
                        Logout
                    </a>
                    <form id="logout-form" action="{{ route('logout') }}" method="POST" class="hidden">
                        @csrf
                    </form>
                </li>
            </ul>
        </div>
    </aside>
    <!-- end sidenav -->

    <main class="ease-soft-in-out xl:ml-68.5 relative h-full max-h-screen rounded-xl transition-all duration-200">
        <!-- Navbar -->
        <nav class="relative flex flex-wrap items-center justify-center px-0 py-2 transition-all shadow-[0_10px_15px_-5px_rgba(0,0,0,0.07)] duration-250 ease-soft-in rounded-2xl lg:flex-nowrap" navbar-main navbar-scroll="true">
            <div class="flex items-center justify-center w-full px-4 py-1 mx-auto flex-wrap-inherit">
                <nav>
                    <h6 class="mb-0 font-bold capitalize text-2xl">@yield('page_title', 'Dashboard')</h6>
                </nav>
            </div>
        </nav>

        <!-- Page Content -->
        <div class="p-6">
            @yield('content')
        </div>
    </main>

    <!-- Plugins -->
    <script src="{{ asset('assets/js/sidenav-burger.js') }}"></script>
    <script src="{{ asset('assets/js/plugins/chartjs.min.js') }}" async></script>
    <script src="{{ asset('assets/js/plugins/perfect-scrollbar.min.js') }}" async></script>
    <script async defer src="https://buttons.github.io/buttons.js"></script>
    <script src="{{ asset('assets/js/soft-ui-dashboard-tailwind.js?v=1.0.5') }}" async></script>
    @yield('scripts')
    @stack('scripts')
</body>
</html>
