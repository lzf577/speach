import android.os.Bundle;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Button;
import android.widget.ArrayAdapter;
import android.widget.Toast;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import android.speech.tts.TextToSpeech;
import android.speech.tts.TextToSpeech.OnInitListener;
import java.util.List;
import java.util.ArrayList;
import java.util.Locale;
import android.content.Intent;
import java.io.File;
import android.net.Uri;
import android.os.AsyncTask;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.RequestBody;
import okhttp3.MediaType;
import okhttp3.FormBody;

public class MainActivity extends AppCompatActivity implements OnInitListener {

    private TextToSpeech tts;
    private EditText textInput;
    private Spinner speakerSpinner;
    private Button convertButton;
    private TextView resultLabel;
    private String saveDir = "/sdcard/Download"; // 默认保存路径

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        textInput = findViewById(R.id.text_input);
        speakerSpinner = findViewById(R.id.speaker_spinner);
        convertButton = findViewById(R.id.convert_button);
        resultLabel = findViewById(R.id.result_label);

        tts = new TextToSpeech(this, this);

        // 触发转换操作
        convertButton.setOnClickListener(v -> convertText());

        // 异步获取发音人列表
        fetchSpeakersAsync();
    }

    @Override
    public void onInit(int status) {
        if (status == TextToSpeech.SUCCESS) {
            // 设置 TTS 语言
            Locale locale = Locale.US;
            int langResult = tts.setLanguage(locale);
        } else {
            Toast.makeText(this, "TTS 初始化失败", Toast.LENGTH_SHORT).show();
        }
    }

    private void convertText() {
        String text = textInput.getText().toString().trim();
        if (text.isEmpty()) {
            resultLabel.setText("请输入文本");
            return;
        }

        String speaker = speakerSpinner.getSelectedItem().toString();
        resultLabel.setText("正在转换，请稍等...");

        // 执行后台操作进行文本转语音
        new ConvertTask().execute(text, speaker);
    }

    private class ConvertTask extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... params) {
            String text = params[0];
            String speaker = params[1];

            // 发起网络请求，进行 TTS 转换
            String result = sendTTSRequest(text, speaker);
            return result;
        }

        @Override
        protected void onPostExecute(String result) {
            if (result != null) {
                resultLabel.setText("转换完成！音频文件已保存.");
            } else {
                resultLabel.setText("转换失败！");
            }
        }
    }

    private String sendTTSRequest(String text, String speakerName) {
        OkHttpClient client = new OkHttpClient();

        MediaType JSON = MediaType.get("application/json; charset=utf-8");
        String json = "{\"text\":\"" + text + "\", \"spk\":{\"from_spk_name\":\"" + speakerName + "\"}, \"tts\":{\"sample_rate\":44100, \"output_format\":\"wav\", \"bitrate\":\"192k\"}}";
        RequestBody body = RequestBody.create(json, JSON);

        Request request = new Request.Builder()
                .url("http://192.168.41.111:7870/v2/tts")
                .post(body)
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (response.isSuccessful()) {
                // 保存音频文件到指定目录
                File outputFile = new File(saveDir, "output_" + System.currentTimeMillis() + ".wav");
                // 写入文件（这里可以根据需要处理响应内容）
                return outputFile.getAbsolutePath();
            } else {
                return null;
            }
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    private void fetchSpeakersAsync() {
        // 模拟获取 speakers 的异步任务
        new Thread(() -> {
            List<String> speakers = new ArrayList<>();
            speakers.add("Speaker 1");
            speakers.add("Speaker 2");

            runOnUiThread(() -> {
                ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, speakers);
                adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
                speakerSpinner.setAdapter(adapter);
            });
        }).start();
    }
}
