import numpy as np
from gnuradio import gr
import pmt

class blk(gr.sync_block):
    def __init__(self, fft_size=1024, avg_frames_base2=64, sample_rate=2e6,
                 symbol_rate=250e3, excess_bw=0.35, report_interval=1):
        gr.sync_block.__init__(
            self,
            name='RRC SNR Detector',
            in_sig=[np.complex64],
            out_sig=[],
        )

        # Parameters
        self.fft_size = fft_size
        self.step = fft_size // 2  # 50% overlap
        self.avg_frames = avg_frames_base2
        self.sample_rate = sample_rate
        self.symbol_rate = symbol_rate
        self.excess_bw = excess_bw
        self.report_interval = float(report_interval)  # in seconds

        # Auto compute how many samples to skip to hit the desired report interval
        samples_for_avg = self.avg_frames * self.step
        total_samples = int(self.report_interval * self.sample_rate)
        self.skip_samples_after_output = max(0, total_samples - samples_for_avg)

        # Internal state
        self.buffer = np.zeros((self.avg_frames, self.fft_size), dtype=np.complex64)
        self.buffer_index = 0
        self.samples_to_skip = 0
        self.residual = np.array([], dtype=np.complex64)

        # Frequency masks for signal and noise regions
        freqs = np.fft.fftfreq(self.fft_size, d=1.0 / self.sample_rate)
        half_bw = self.symbol_rate / 2
        trans_bw = self.symbol_rate * (1 + self.excess_bw) / 2
        self.signal_mask = np.abs(freqs) <= half_bw
        self.noise_mask = np.abs(freqs) > trans_bw
        self.normalizer_signal = np.count_nonzero(self.signal_mask)
        self.normalizer_noise = np.count_nonzero(self.noise_mask)

        self.message_port_register_out(pmt.intern("snr_out"))

    def work(self, input_items, output_items):
        in0 = np.concatenate((self.residual, input_items[0]))

        # Skip processing if in skip window
        if self.samples_to_skip > 0:
            to_consume = min(len(in0), self.samples_to_skip)
            self.samples_to_skip -= to_consume
            self.residual = in0[to_consume:]
            return len(input_items[0])

        i = 0
        while i + self.fft_size <= len(in0):
            window = in0[i:i+self.fft_size]
            fft_result = np.fft.fftshift(np.fft.fft(window) / np.sqrt(self.fft_size))
            self.buffer[self.buffer_index % self.avg_frames] = fft_result
            self.buffer_index += 1
            i += self.step

            if self.buffer_index >= self.avg_frames:
                avg_fft = np.mean(np.abs(self.buffer)**2, axis=0)
                signal_power = np.sum(avg_fft[self.signal_mask]) / self.normalizer_signal
                noise_power = np.sum(avg_fft[self.noise_mask]) / self.normalizer_noise
                snr = signal_power / (noise_power + 1e-12)
                snr_db = abs(10 * np.log10(snr))

                msg = pmt.cons(pmt.intern("snr"), pmt.from_double(snr_db))
                msg_type = pmt.intern("snr_out")
                self.message_port_pub(msg_type, msg)

                # Reset buffer and enter skip mode
                self.buffer_index = 0
                self.samples_to_skip = self.skip_samples_after_output
                break  # break loop to enforce skip window

        self.residual = in0[i:]
        return len(input_items[0])
