%% Visualization Script: Risk-Neutral PDF for multiple tenors
% Plots the probability density function of S(T) for selected tenors.

% 1. Setup
[spot, lag, days, domdfs, fordfs, vols, cps, deltas] = getMarket();
tau = lag / 365;
Ts = days / 365;

domCurve = makeDepoCurve(Ts, domdfs);
forCurve = makeDepoCurve(Ts, fordfs);
fwdCurve = makeFwdCurve(domCurve, forCurve, spot, tau);
volSurf = makeVolSurface(fwdCurve, Ts, cps, deltas, vols);

% 2. Select tenors to plot: 7D, 59D, 365D, 730D
tenor_idx = [1, 5, 8, 10];
colors = {'b', 'r', [0 0.6 0], [0.8 0 0.8]};

figure('Name', 'Risk-Neutral PDFs', 'Position', [100, 100, 900, 550]);

for j = 1:length(tenor_idx)
    idx = tenor_idx(j);
    T = Ts(idx);
    fwd = getFwdSpot(fwdCurve, T);
    
    K_range = linspace(fwd * 0.5, fwd * 1.6, 400);
    pdf_vals = getPdf(volSurf, T, K_range);
    
    plot(K_range, pdf_vals, '-', 'Color', colors{j}, 'LineWidth', 2); hold on;
end

title('Risk-Neutral Probability Density Functions \phi_{S_T}(x)', 'FontSize', 14);
xlabel('Spot Price S_T', 'FontSize', 12);
ylabel('Probability Density', 'FontSize', 12);
legend(arrayfun(@(i) sprintf('%d Days', days(i)), tenor_idx, 'UniformOutput', false), ...
    'Location', 'best');
grid on;
