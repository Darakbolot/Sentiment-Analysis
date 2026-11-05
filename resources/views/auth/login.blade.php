<x-guest-layout>
    <div class="w-full max-w-2xl bg-white p-10 rounded-2xl shadow-lg" name="login-form">

        <div class="text-center mb-8">
            <h2 class="text-2xl font-bold text-gray-800">Login</h2>
        </div>

        <x-auth-session-status class="mb-4" :status="session('status')" />

        {{-- [DIUBAH] Menghapus class="p-5" dari form --}}
        <form method="POST" action="{{ route('login') }}">
            @csrf

            <div>
                <x-input-label for="email" :value="__('Email')" />
                <x-text-input id="email" class="block mt-1 w-full" type="email" name="email" :value="old('email')" required autofocus autocomplete="username" />
                <x-input-error :messages="$errors->get('email')" class="mt-2" />
            </div>

            <div class="mt-4">
                <x-input-label for="password" :value="__('Password')" />
                <x-text-input id="password" class="block mt-1 w-full"
                                type="password"
                                name="password"
                                required autocomplete="current-password" />
                <x-input-error :messages="$errors->get('password')" class="mt-2" />
            </div>

            <div class="flex items-center justify-between mt-4 text-sm">
                <label for="remember_me" class="inline-flex items-center">
                    <input id="remember_me" type="checkbox" class="rounded border-gray-300 text-blue-600 shadow-sm focus:ring-blue-500" name="remember">
                    <span class="ms-2 text-gray-600">{{ __('Ingat saya') }}</span>
                </label>

                @if (Route::has('password.request'))
                    <a class="underline text-gray-600 hover:text-gray-900 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500" href="{{ route('password.request') }}">
                        {{ __('Lupa password?') }}
                    </a>
                @endif
            </div>

            <div class="mt-8">
                <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-full hover:bg-blue-700 shadow-lg transform hover:scale-105 transition-transform duration-300">
                    {{ __('Masuk') }}
                </button>
            </div>
        </form>
    </div>
</x-guest-layout>