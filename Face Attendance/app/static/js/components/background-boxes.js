import { cn } from '../lib/utils.js';

class BackgroundBoxes {
    constructor(container) {
        this.container = container;
        this.rows = new Array(150).fill(1);
        this.cols = new Array(100).fill(1);
        this.colors = [
            'rgb(125, 211, 252)',  // sky-300
            'rgb(249, 168, 212)',  // pink-300
            'rgb(134, 239, 172)',  // green-300
            'rgb(253, 224, 71)',   // yellow-300
            'rgb(252, 165, 165)',  // red-300
            'rgb(216, 180, 254)',  // purple-300
            'rgb(147, 197, 253)',  // blue-300
            'rgb(165, 180, 252)',  // indigo-300
            'rgb(196, 181, 253)',  // violet-300
        ];
        this.init();
    }

    getRandomColor() {
        return this.colors[Math.floor(Math.random() * this.colors.length)];
    }

    createBoxes() {
        const boxesContainer = document.createElement('div');
        boxesContainer.className = cn(
            'absolute left-1/4 p-4 -top-1/4 flex -translate-x-1/2 -translate-y-1/2 w-full h-full z-0'
        );
        boxesContainer.style.transform = 'translate(-40%,-60%) skewX(-48deg) skewY(14deg) scale(0.675) rotate(0deg) translateZ(0)';

        this.rows.forEach((_, i) => {
            const row = document.createElement('div');
            row.className = 'w-16 h-8 border-l border-slate-700 relative';

            this.cols.forEach((_, j) => {
                const col = document.createElement('div');
                col.className = 'w-16 h-8 border-r border-t border-slate-700 relative';

                // Add hover effect
                col.addEventListener('mouseenter', () => {
                    col.style.backgroundColor = this.getRandomColor();
                    col.style.transition = 'background-color 0s';
                });

                col.addEventListener('mouseleave', () => {
                    col.style.backgroundColor = '';
                    col.style.transition = 'background-color 2s';
                });

                // Add plus sign for every other box
                if (j % 2 === 0 && i % 2 === 0) {
                    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                    svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
                    svg.setAttribute('fill', 'none');
                    svg.setAttribute('viewBox', '0 0 24 24');
                    svg.setAttribute('stroke-width', '1.5');
                    svg.setAttribute('stroke', 'currentColor');
                    svg.className = 'absolute h-6 w-10 -top-[14px] -left-[22px] text-slate-700 stroke-[1px] pointer-events-none';

                    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                    path.setAttribute('stroke-linecap', 'round');
                    path.setAttribute('stroke-linejoin', 'round');
                    path.setAttribute('d', 'M12 6v12m6-6H6');

                    svg.appendChild(path);
                    col.appendChild(svg);
                }

                row.appendChild(col);
            });

            boxesContainer.appendChild(row);
        });

        this.container.appendChild(boxesContainer);
    }

    init() {
        this.createBoxes();
    }
}

export { BackgroundBoxes }; 