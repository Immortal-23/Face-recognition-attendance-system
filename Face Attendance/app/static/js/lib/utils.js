// utils.js
function clsx(...inputs) {
    return inputs
        .filter(Boolean)
        .join(' ');
}

function twMerge(...inputs) {
    return inputs
        .filter(Boolean)
        .join(' ');
}

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export { cn, clsx, twMerge }; 