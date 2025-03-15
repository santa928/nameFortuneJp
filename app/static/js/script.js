document.addEventListener('DOMContentLoaded', function() {
    const fortuneForm = document.getElementById('fortune-form');
    const resultSection = document.getElementById('result-section');
    const resultName = document.getElementById('result-name');

    fortuneForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const lastName = document.getElementById('last-name').value.trim();
        const firstName = document.getElementById('first-name').value.trim();
        const gender = document.querySelector('input[name="gender"]:checked').value;
        
        if (!lastName || !firstName) {
            alert('姓名を入力してください');
            return;
        }
        
        // ローディング表示
        const submitButton = this.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = '取得中...';
        
        // 結果セクションを非表示
        resultSection.style.display = 'none';
        
        // APIリクエスト
        fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                last_name: lastName,
                first_name: firstName,
                gender: gender
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('サーバーエラーが発生しました');
            }
            return response.json();
        })
        .then(data => {
            // ボタンを元に戻す
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
            
            if (data.error) {
                alert('エラー: ' + data.error);
                return;
            }
            
            displayResults(lastName, firstName, gender, data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('エラーが発生しました: ' + error.message);
            
            // ボタンを元に戻す
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        });
    });

    function displayResults(lastName, firstName, gender, data) {
        // 名前を表示
        const genderText = gender === 'm' ? '男性' : '女性';
        resultName.textContent = lastName + firstName + 'さん（' + genderText + '）の姓名判断結果';
        
        // 各運勢の結果を表示
        const fortuneTypes = {
            '天格': 'tenkaku',
            '人格': 'jinkaku',
            '地格': 'jikaku',
            '外格': 'gaikaku',
            '総格': 'soukaku'
        };
        
        // 既存の説明文を削除
        document.querySelectorAll('.result-description').forEach(el => el.remove());
        
        // 結果を表示
        Object.entries(fortuneTypes).forEach(([type, id]) => {
            const resultDiv = document.getElementById(`${id}-result`);
            if (resultDiv && data[type]) {
                const valueElement = resultDiv.querySelector('.result-value');
                const fortuneElement = resultDiv.querySelector('.result-fortune');
                
                // 運勢を表示
                fortuneElement.textContent = data[type];
                setFortuneClass(fortuneElement, data[type]);
                
                // 説明文を追加
                if (data[`${type}_説明`]) {
                    const descriptionElement = document.createElement('p');
                    descriptionElement.className = 'result-description';
                    descriptionElement.textContent = data[`${type}_説明`];
                    resultDiv.appendChild(descriptionElement);
                }
            }
        });
        
        // 三才配置の結果を表示
        const sansaiResult = document.getElementById('sansai-result');
        if (sansaiResult) {
            const valueElement = sansaiResult.querySelector('.result-value');
            const fortuneElement = sansaiResult.querySelector('.result-fortune');
            
            // 配置パターンを表示
            if (data['三才配置']) {
                valueElement.textContent = `配置: ${data['三才配置']}`;
            }
            
            // 運勢を表示
            if (data['三才配置_運勢']) {
                fortuneElement.textContent = data['三才配置_運勢'];
                setFortuneClass(fortuneElement, data['三才配置_運勢']);
            }
            
            // 説明文を追加
            if (data['三才配置_説明']) {
                const descriptionElement = document.createElement('p');
                descriptionElement.className = 'result-description';
                descriptionElement.textContent = data['三才配置_説明'];
                sansaiResult.appendChild(descriptionElement);
            }
        }
        
        // 結果セクションを表示
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    function setFortuneClass(element, fortune) {
        // クラスをリセット
        element.classList.remove('daikichi', 'chukichi', 'shokichi', 'kichi', 'suekichi', 'kyo', 'daikyo', 'hankichi', 'hankyo');
        
        // 運勢に応じたクラスを追加
        const fortuneClasses = {
            '大吉': 'daikichi',
            '中吉': 'chukichi',
            '小吉': 'shokichi',
            '吉': 'kichi',
            '末吉': 'suekichi',
            '凶': 'kyo',
            '大凶': 'daikyo',
            '半吉': 'hankichi',
            '半凶': 'hankyo'
        };
        
        const className = fortuneClasses[fortune];
        if (className) {
            element.classList.add(className);
        }
    }
}); 