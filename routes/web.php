<?php

use App\Http\Controllers\ProfileController;
use App\Http\Controllers\WordCloudController;

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::prefix('admin')->middleware('auth')->group(function () {
    Route::get('/wordcloud', [WordCloudController::class, 'index'])->name('wordcloud.index');
    Route::get('/wordcloud/data', [WordCloudController::class, 'getData'])->name('wordcloud.data');
    Route::get('/wordcloud/detail/{source}/{sentiment}/{keyword}', [WordCloudController::class, 'getDetail'])->name('wordcloud.detail');
    Route::get('wordcloud/config', [App\Http\Controllers\WordCloudController::class, 'config'])->name('wordcloud.config');
    Route::post('wordcloud/config/save', [App\Http\Controllers\WordCloudController::class, 'saveConfig'])->name('wordcloud.config.save');
});

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

require __DIR__.'/auth.php';
