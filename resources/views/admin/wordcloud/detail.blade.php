@extends('layouts.admin')

@section('title', 'Detail Kata - '.$keyword)
@section('page_title', 'Detail Kata Kunci')

@section('content')
@php
    $count = $data->count();

    // Menentukan kelas warna berdasarkan sentimen untuk tampilan visual
    $sentimentColors = [
        'positif' => ['bg' => 'bg-green-100', 'text' => 'text-green-800'],
        'netral'  => ['bg' => 'bg-gray-100',  'text' => 'text-gray-800'],
        'negatif' => ['bg' => 'bg-red-100',   'text' => 'text-red-800'],
    ];
    $colorClass = $sentimentColors[$sentiment] ?? $sentimentColors['netral'];
@endphp

<div class="bg-sky-100 p-6 rounded-2xl shadow-lg">

    <div class="flex justify-between items-center mb-4">
        <a href="{{ route('wordcloud.index') }}"
           class="inline-flex items-center px-4 py-2 bg-white text-gray-700 font-semibold rounded-lg shadow-sm hover:bg-gray-100 transition-colors duration-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clip-rule="evenodd" />
            </svg>
            Kembali
        </a>

        <div class="text-center">
            <h2 class="text-3xl font-bold text-gray-800 break-words">"{{ ucfirst($keyword) }}"</h2>
            <div class="mt-2 flex items-center justify-center gap-x-4">
                <span class="inline-block bg-blue-100 text-blue-800 px-4 py-1 text-sm font-semibold rounded-full">{{ ucfirst($source) }}</span>
                <span class="inline-block {{ $colorClass['bg'] }} {{ $colorClass['text'] }} px-4 py-1 text-sm font-semibold rounded-full">{{ ucfirst($sentiment) }}</span>
            </div>
        </div>

        <div class="invisible">
            <a href="#" class="inline-flex items-center px-4 py-2 bg-white text-gray-700 font-semibold rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clip-rule="evenodd" />
                </svg>
                Kembali
            </a>
        </div>
    </div>

    <p class="text-center text-gray-600 mb-6">
        Ditemukan total <strong class="text-gray-800">{{ $count }}</strong> data yang relevan.
    </p>

    <div class="bg-white rounded-xl shadow p-4 sm:p-6">
        @if($count == 0)
            <div class="p-4 bg-yellow-100 text-yellow-800 rounded-lg text-center">
                Tidak ada data relevan yang dapat ditampilkan untuk kata kunci ini.
            </div>
        @else
            <div class="overflow-x-auto">
                {{-- TABEL UNTUK MEDSOS --}}
                @if($source === 'medsos')
                    <table class="w-full text-sm">
                        <thead class="bg-gray-100 text-gray-600 uppercase">
                            <tr>
                                <th class="px-6 py-3 text-center w-16">No</th>
                                <th class="px-6 py-3 text-left">Caption</th>
                                <th class="px-6 py-3 text-left">Comment</th>
                                <th class="px-6 py-3 text-center w-24">Link</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                            @foreach($data as $i => $row)
                                <tr class="hover:bg-gray-50">
                                    <td class="px-6 py-4 text-center font-medium text-gray-500">{{ $i + 1 }}</td>
                                    <td class="px-6 py-4 break-words prose prose-sm max-w-md">{{ $row->caption ?? '-' }}</td>
                                    <td class="px-6 py-4 break-words prose prose-sm max-w-md">{{ $row->comment ?? '-' }}</td>
                                    <td class="px-6 py-4 text-center">
                                        @if(!empty($row->link))
                                            <a href="{{ $row->link }}" target="_blank" class="font-medium text-indigo-600 hover:underline">Lihat</a>
                                        @else
                                            <span>-</span>
                                        @endif
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                @endif

                {{-- TABEL UNTUK BERITA --}}
                @if($source === 'berita')
                    <table class="w-full text-sm">
                        <thead class="bg-gray-100 text-gray-600 uppercase">
                            <tr>
                                <th class="px-6 py-3 text-center w-16">No</th>
                                <th class="px-6 py-3 text-left">Judul</th>
                                <th class="px-6 py-3 text-left">Isi Berita</th>
                                <th class="px-6 py-3 text-left">Tag</th>
                                <th class="px-6 py-3 text-center w-24">Link</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                            @foreach($data as $i => $row)
                                <tr class="hover:bg-gray-50">
                                    <td class="px-6 py-4 text-center font-medium text-gray-500">{{ $i + 1 }}</td>
                                    <td class="px-6 py-4 font-semibold break-words max-w-xs">{{ $row->judul ?? '-' }}</td>
                                    <td class="px-6 py-4 break-words prose prose-sm max-w-md">{{ $row->isi_berita ?? '-' }}</td>
                                    <td class="px-6 py-4 text-gray-600">{{ $row->tag ?? '-' }}</td>
                                    <td class="px-6 py-4 text-center">
                                        @if(!empty($row->link))
                                            <a href="{{ $row->link }}" target="_blank" class="font-medium text-indigo-600 hover:underline">Lihat</a>
                                        @else
                                            <span>-</span>
                                        @endif
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                @endif
            </div>
        @endif
    </div>

    </div>
@endsection
