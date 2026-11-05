@extends('layouts.admin')

@section('title', 'Word Cloud')
@section('page_title', 'Word Cloud')

@section('content')

{{-- Custom CSS untuk background Mega Mendung --}}
<style>
.bg-megamendung {
    position: relative;
    overflow: hidden;
    /* Warna dasar yang setara dengan bg-sky-100 */
    background-color: #e0f2fe;
}

/* Pseudo-element untuk layer background agar tidak mengganggu konten */
.bg-megamendung::before {
    content: '';
    position: absolute;
    inset: 0;

    background-image: url("{{ asset('assets/img/red-ornament-batik-mega-mendung-cirebon-indonesia-with-transparent-background-png.png') }}");
    background-repeat: no-repeat;

    /* GANTI BARIS INI:
      Gunakan nilai X dan Y yang negatif untuk menarik gambar ke kiri dan ke atas.
      Nilai pertama adalah untuk geser horizontal (kiri/kanan).
      Nilai kedua adalah untuk geser vertikal (atas/bawah).
    */
    background-position: -10px -40px; /* <-- CONTOH NILAI, SILAKAN DISESUAIKAN */

    /* Ukuran motif besar */
    background-size: 300px auto;

    z-index: 0;
    /* opacity: 0.15; */
}

/* Animasi halus untuk background (opsional) */
@keyframes subtle-shift {
    0%, 100% {
        background-position: 0 0, 100px 60px;
    }
    50% {
        background-position: 5px 3px, 105px 63px;
    }
}

/* Pastikan semua konten di dalam div berada di atas layer background */
.bg-megamendung > * {
    position: relative;
    z-index: 1;
}

/* Penyesuaian untuk responsiveness */
@media (max-width: 768px) {
    .bg-megamendung::before {
        background-size: 180px auto, 180px auto, 180px auto, 180px auto;
    }
}

@media (max-width: 480px) {
    .bg-megamendung::before {
        background-size: 140px auto, 140px auto, 140px auto, 140px auto;
    }
}

/* Styling tambahan untuk meningkatkan visual */
.wordcloud-container {
    backdrop-filter: blur(1px);
    transition: all 0.3s ease;
}

.wordcloud-container:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 25px -5px rgba(0,0,0,0.15);
}

.section-title {
    display: inline-block;
    background: white;
    padding: 0.5rem 1.5rem;
    border-radius: 9999px; /* rounded-full */
    font-weight: bold;
    font-size: 1.25rem; /* text-xl */
    color: #334155; /* text-slate-700 */
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border: 1px solid #f1f5f9; /* border-slate-100 */
}

.section-title-wrapper {
    text-align: center;
    margin-bottom: 2rem;
}

</style>

<div class="space-y-8">

    {{-- SECTION MEDSOS --}}
    <div class="bg-megamendung p-4 md:p-6 rounded-2xl shadow-[0_10px_15px_-5px_rgba(0,0,0,0.1)] wordcloud-container">
        <h2 class="section-title-wrapper">
            <span class="section-title">Word Cloud - Media Sosial</span>
        </h2>
        <div class="dynamic-grid grid gap-8 items-start" data-source="medsos">
            <div data-sentiment="positif">
                <div class="text-center mb-4">
                    <h3 class="inline-block bg-white px-6 py-2 rounded-full font-bold text-lg text-green-600 shadow-sm border border-green-100">
                        Positif
                    </h3>
                </div>
                <div id="wordcloud-medsos-positif" class="w-full max-w-xs mx-auto aspect-square rounded-full overflow-hidden flex items-center justify-center text-gray-500 bg-opacity-70 bg-white shadow-inner border-2 border-white">
                    Loading...
                </div>
            </div>
            <div data-sentiment="netral">
                <div class="text-center mb-4">
                    <h3 class="inline-block bg-white px-6 py-2 rounded-full font-bold text-lg text-gray-600 shadow-sm border border-gray-100">
                        Netral
                    </h3>
                </div>
                <div id="wordcloud-medsos-netral" class="w-full max-w-xs mx-auto aspect-square rounded-full overflow-hidden flex items-center justify-center text-gray-500 bg-opacity-70 bg-white shadow-inner border-2 border-white">
                    Loading...
                </div>
            </div>
            <div data-sentiment="negatif">
                <div class="text-center mb-4">
                    <h3 class="inline-block bg-white px-6 py-2 rounded-full font-bold text-lg text-red-600 shadow-sm border border-red-100">
                        Negatif
                    </h3>
                </div>
                <div id="wordcloud-medsos-negatif" class="w-full max-w-xs mx-auto aspect-square rounded-full overflow-hidden flex items-center justify-center text-gray-500 bg-opacity-70 bg-white shadow-inner border-2 border-white">
                    Loading...
                </div>
            </div>
        </div>
    </div>

    {{-- SECTION BERITA --}}
    <div class="bg-megamendung p-4 md:p-6 rounded-2xl shadow-[0_10px_15px_-5px_rgba(0,0,0,0.1)] wordcloud-container">
        <h2 class="section-title-wrapper">
            <span class="section-title">Word Cloud - Berita</span>
        </h2>
        <div class="dynamic-grid grid gap-8 items-start" data-source="berita">
            <div data-sentiment="positif">
                <div class="text-center mb-4">
                    <h3 class="inline-block bg-white px-6 py-2 rounded-full font-bold text-lg text-green-600 shadow-sm border border-green-100">
                        Positif
                    </h3>
                </div>
                <div id="wordcloud-berita-positif" class="w-full max-w-xs mx-auto aspect-square rounded-full overflow-hidden flex items-center justify-center text-gray-500 bg-opacity-70 bg-white shadow-inner border-2 border-white">
                    Loading...
                </div>
            </div>
            <div data-sentiment="netral">
                <div class="text-center mb-4">
                    <h3 class="inline-block bg-white px-6 py-2 rounded-full font-bold text-lg text-gray-600 shadow-sm border border-gray-100">
                        Netral
                    </h3>
                </div>
                <div id="wordcloud-berita-netral" class="w-full max-w-xs mx-auto aspect-square rounded-full overflow-hidden flex items-center justify-center text-gray-500 bg-opacity-70 bg-white shadow-inner border-2 border-white">
                    Loading...
                </div>
            </div>
            <div data-sentiment="negatif">
                <div class="text-center mb-4">
                    <h3 class="inline-block bg-white px-6 py-2 rounded-full font-bold text-lg text-red-600 shadow-sm border border-red-100">
                        Negatif
                    </h3>
                </div>
                <div id="wordcloud-berita-negatif" class="w-full max-w-xs mx-auto aspect-square rounded-full overflow-hidden flex items-center justify-center text-gray-500 bg-opacity-70 bg-white shadow-inner border-2 border-white">
                    Loading...
                </div>
            </div>
        </div>
    </div>
</div>
@endsection

@section('scripts')
<script src="https://d3js.org/d3.v5.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-cloud/build/d3.layout.cloud.min.js"></script>

<script>
const detailUrlTemplate = "{{ route('wordcloud.detail', ['source' => '__SOURCE__', 'sentiment' => '__SENTIMENT__', 'keyword' => '__KEYWORD__']) }}";
const wordcloudData = @json($wordcloudData ?? [], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

function adjustGridLayouts() {

    function getSizeCategory(count) {
        if (count >= 100) return 'super';
        if (count >= 50) return 'large';
        if (count >= 15) return 'medium';
        return 'normal';
    }

    const sizeClasses = {
        normal: 'max-w-sm',
        medium: 'max-w-xl',
        large: 'max-w-2xl',
        super: 'max-w-none'
    };

    document.querySelectorAll('.dynamic-grid').forEach(grid => {
        const source = grid.dataset.source;
        const items = {
            positif: grid.querySelector('[data-sentiment="positif"]'),
            netral: grid.querySelector('[data-sentiment="netral"]'),
            negatif: grid.querySelector('[data-sentiment="negatif"]')
        };

        const counts = {
            positif: (wordcloudData[source]?.positif || []).length,
            netral: (wordcloudData[source]?.netral || []).length,
            negatif: (wordcloudData[source]?.negatif || []).length
        };

        const sizes = {
            positif: getSizeCategory(counts.positif),
            netral: getSizeCategory(counts.netral),
            negatif: getSizeCategory(counts.negatif),
        };

        // [LOGIKA DIPERBAIKI]
        // Langkah 1: Atur kelas ukuran individu untuk setiap word cloud
        Object.entries(sizes).forEach(([sentiment, sizeCategory]) => {
            const cloudContainer = items[sentiment].querySelector('[id^="wordcloud-"]');
            if (cloudContainer) {
                // Selalu hapus semua kemungkinan kelas ukuran lama untuk reset
                Object.values(sizeClasses).forEach(cls => cloudContainer.classList.remove(cls));
                // Selalu tambahkan kelas yang benar, termasuk 'max-w-none'
                cloudContainer.classList.add(sizeClasses[sizeCategory]);
            }
        });

        const hasLargeOrSuper = Object.values(sizes).some(s => s === 'large' || s === 'super');

        grid.className = 'dynamic-grid grid gap-8 items-start'; // Reset

        if (hasLargeOrSuper) {
            grid.classList.add('grid-cols-1');
        } else {
            grid.classList.add('grid-cols-1', 'sm:grid-cols-2', 'lg:grid-cols-3');
        }
    });
}

function runDashboard() {
    adjustGridLayouts();
    setTimeout(initWordClouds, 50);
}

const debouncedRun = debounce(runDashboard, 250);
window.addEventListener('load', runDashboard);
window.addEventListener('resize', debouncedRun);

// --- Fungsi-fungsi helper (tidak diubah) ---
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => { clearTimeout(timeout); func(...args); };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
function initWordClouds() {
    const sources = ["berita", "medsos"];
    const sentiments = ["positif", "netral", "negatif"];
    sources.forEach(src => {
        sentiments.forEach(sent => {
            const items = wordcloudData[src] && wordcloudData[src][sent] ? wordcloudData[src][sent] : [];
            renderWordCloud(`#wordcloud-${src}-${sent}`, items, src, sent);
        });
    });
}
function renderWordCloud(selector, items, source, sentiment) {
    const el = document.querySelector(selector);
    if (!el) return;
    el.innerHTML = "";
    el.classList.remove('flex', 'items-center', 'justify-center');
    if (!items || items.length === 0) {
        el.textContent = "Tidak ada data";
        el.classList.add('text-gray-400', 'flex', 'items-center', 'justify-center');
        return;
    }
    const weights = items.map(i => Number(i.weight || 0));
    const minWeight = Math.min(...weights);
    const maxWeight = Math.max(...weights);
    const minPx = 16;
    const maxPx = 45;
    let scale;
    if (minWeight === maxWeight) {
        scale = () => (minPx + maxPx) / 2;
    } else {
        scale = d3.scaleSqrt().domain([minWeight, maxWeight]).range([minPx, maxPx]);
    }
    const containerPadding = 40;
    const fullDimension = Math.min(el.clientWidth, el.clientHeight);
    if (fullDimension <= 0) return;
    const layoutDimension = fullDimension - (containerPadding * 2);
    if (layoutDimension <= 0) return;
    const wordsForLayout = items.map(item => ({ text: item.text, size: scale(item.weight) }));
    const layout = d3.layout.cloud()
        .size([layoutDimension, layoutDimension])
        .words(wordsForLayout)
        .padding(5)
        .rotate(() => (Math.random() > 0.8) ? 90 : 0)
        .font("Impact")
        .fontSize(d => d.size)
        .on("end", draw);
    layout.start();
    function draw(wordsArr) {
        const svg = d3.select(selector).append("svg")
            .attr("width", fullDimension)
            .attr("height", fullDimension)
            .attr('viewBox', `0 0 ${fullDimension} ${fullDimension}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');
        const g = svg.append("g")
            .attr("transform", `translate(${fullDimension / 2},${fullDimension / 2})`);
        const color = d3.scaleOrdinal(d3.schemeCategory10);
        g.selectAll("text").data(wordsArr).enter().append("text")
            .style("font-size", d => `${d.size}px`)
            .style("font-family", "Impact")
            .style("fill", (d, i) => color(i))
            .attr("text-anchor", "middle")
            .attr("transform", d => `translate(${d.x},${d.y})rotate(${d.rotate})`)
            .style("cursor", "pointer")
            .text(d => d.text)
            .on("mouseover", function(d) {
                if (!d) return;
                d3.select(this).transition().duration(150).style("font-size", `${d.size * 1.1}px`).style("fill", "#2563eb");
            })
            .on("mouseout", function(d, i) {
                if (!d) return;
                d3.select(this).transition().duration(150).style("font-size", `${d.size}px`).style("fill", color(i));
            })
            .on("click", function(d) {
                if (!d || !d.text) { console.error("Objek data tidak valid saat diklik."); return; }
                const keyword = d.text;
                let url = detailUrlTemplate.replace('__SOURCE__', encodeURIComponent(source));
                url = url.replace('__SENTIMENT__', encodeURIComponent(sentiment));
                url = url.replace('__KEYWORD__', encodeURIComponent(keyword));
                window.location.href = url;
            });
    }
}
</script>
@endsection
